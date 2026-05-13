"""
Lab 3 — Part A: Multimodal Movie Genre Classifier
==================================================
Complete this file to build and train your multimodal neural network.
How you structure the training script (entry point, argument handling, etc.)
is up to you.

Architecture:
  ImageBranch   — 4 ConvBlocks (3→32→64→128→256) + AdaptiveAvgPool → Linear(256)
  TabularBranch — numeric FC sub-branch + embedding sub-branch (max-pool) → merge
  FusionHead    — concat(image, tabular) → Dropout → Linear(256) → Linear(6)
"""

import json
import os
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
from PIL import Image
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms
from tqdm import tqdm


# =============================================================================
# Constants — adjust these to control model complexity
# =============================================================================

GENRES = ["Animation", "Comedy", "Documentary", "Horror", "Romance", "Sci-Fi"]

NUMERIC_COLS = ["runtime", "vote_average", "vote_count",
                "release_year", "popularity", "budget", "revenue"]

# Pipe-separated list fields — each gets its own embedding vocabulary
LIST_FIELDS = ["cast", "directors", "writers", "production_companies"]

# Single-value categorical fields
SINGLE_CAT_FIELDS = ["mpaa_rating"]

IMAGE_SIZE   = 128   # poster resize target (pixels)
MAX_LIST_LEN = 20    # pad/truncate list fields to this many tokens
TOP_N_VOCAB  = 50    # keep only top-N tokens per field by training frequency
EMBED_DIM    = 32    # embedding dimension for all categorical fields

# --- Paths (relative to this file) ---
_HERE     = Path(__file__).resolve().parent
DATA_DIR  = _HERE.parent.parent / "data" / "movie_posters"
IMAGE_DIR = DATA_DIR / "images"
CKPT_DIR  = _HERE.parent.parent / "models"

# --- Training hyper-parameters ---
BATCH_SIZE   = 64
NUM_EPOCHS   = 25
LR           = 5e-4
WEIGHT_DECAY = 1e-3
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


# =============================================================================
# PROVIDED: VocabBuilder
# =============================================================================

class VocabBuilder:
    """
    Builds integer vocabularies for pipe-separated categorical fields.
    Fit ONLY on training data — fitting on val/test is data leakage.

    Token index conventions:
        0 = <PAD>  — padding
        1 = <UNK>  — unknown token (not in top-N at training time)
        2+ = actual tokens, ordered by training frequency
    """

    PAD_IDX = 0
    UNK_IDX = 1

    def __init__(self, top_n=TOP_N_VOCAB):
        self.top_n  = top_n
        self.vocabs = {}
        self.sizes  = {}

    def fit(self, df):
        for field in LIST_FIELDS:
            if field not in df.columns:
                continue
            counts = Counter()
            for val in df[field].dropna():
                if val:
                    counts.update(v.strip() for v in str(val).split("|") if v.strip())
            top_tokens = [tok for tok, _ in counts.most_common(self.top_n)]
            vocab = {tok: idx + 2 for idx, tok in enumerate(top_tokens)}
            self.vocabs[field] = vocab
            self.sizes[field]  = len(vocab) + 2

        for field in SINGLE_CAT_FIELDS:
            if field not in df.columns:
                continue
            unique_vals = [v for v in df[field].unique()
                           if isinstance(v, str) and v.strip()]
            vocab = {v: idx + 2 for idx, v in enumerate(sorted(unique_vals))}
            self.vocabs[field] = vocab
            self.sizes[field]  = len(vocab) + 2
        return self

    def encode_list(self, val, field, max_len=MAX_LIST_LEN):
        vocab = self.vocabs.get(field, {})
        if not isinstance(val, str) or not val.strip():
            return [self.PAD_IDX] * max_len
        tokens = [v.strip() for v in val.split("|") if v.strip()]
        ids = [vocab.get(tok, self.UNK_IDX) for tok in tokens]
        ids = ids[:max_len]
        ids += [self.PAD_IDX] * (max_len - len(ids))
        return ids

    def encode_single(self, val, field):
        vocab = self.vocabs.get(field, {})
        if not isinstance(val, str) or not val.strip():
            return self.PAD_IDX
        return vocab.get(val.strip(), self.UNK_IDX)

    def save(self, path):
        data = {"vocabs": self.vocabs, "sizes": self.sizes, "top_n": self.top_n}
        Path(path).write_text(json.dumps(data))

    @classmethod
    def load(cls, path):
        data = json.loads(Path(path).read_text())
        vb = cls(top_n=data["top_n"])
        vb.vocabs = data["vocabs"]
        vb.sizes  = data["sizes"]
        return vb


# =============================================================================
# PROVIDED: NumericScaler
# =============================================================================

class NumericScaler:
    """
    Standardises numeric features to zero mean, unit variance.
    Fit on training data only. Missing values are imputed with the training mean.
    """

    def __init__(self):
        self.means = {}
        self.stds  = {}

    def fit(self, df):
        for col in NUMERIC_COLS:
            if col in df.columns:
                vals = pd.to_numeric(df[col], errors="coerce")
                self.means[col] = float(vals.mean())
                self.stds[col]  = max(float(vals.std()), 1e-8)
        return self

    def transform(self, df):
        result = {}
        for col in NUMERIC_COLS:
            vals = pd.to_numeric(df[col], errors="coerce") if col in df.columns \
                   else pd.Series([float("nan")] * len(df))
            vals = vals.fillna(self.means.get(col, 0.0))
            mean = self.means.get(col, 0.0)
            std  = self.stds.get(col, 1.0)
            result[col] = ((vals - mean) / std).values.astype(np.float32)
        return result

    def save(self, path):
        Path(path).write_text(json.dumps({"means": self.means, "stds": self.stds}))

    @classmethod
    def load(cls, path):
        data = json.loads(Path(path).read_text())
        ns = cls()
        ns.means = data["means"]
        ns.stds  = data["stds"]
        return ns


# =============================================================================
# YOUR CODE: Dataset
# =============================================================================

class MoviePosterDataset(Dataset):
    """
    Loads a split (train / val / test) and returns one sample per film.

    Returns (image_tensor, numeric_tensor, cat_fields_dict, label_tensor)
    where cat_fields_dict maps each field name to a long tensor of token ids.
    """

    def __init__(self, df, image_dir, vocab_builder, numeric_scaler,
                 transform=None):
        self.df            = df.reset_index(drop=True)
        self.image_dir     = Path(image_dir)
        self.vocab_builder = vocab_builder
        self.transform     = transform
        # Pre-scale all numeric features once — avoids recomputing per sample
        self.scaled_numeric = numeric_scaler.transform(self.df)
        # Pre-encode labels
        self.labels = [GENRES.index(g) for g in self.df["label"]]

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        row = self.df.iloc[idx]

        # --- Image ---
        img_path = self.image_dir / row["image_path"]
        try:
            img = Image.open(img_path).convert("RGB")
        except Exception:
            img = Image.new("RGB", (IMAGE_SIZE, IMAGE_SIZE), (128, 128, 128))
        if self.transform:
            img = self.transform(img)

        # --- Numeric ---
        numeric = torch.tensor(
            [self.scaled_numeric[col][idx] for col in NUMERIC_COLS],
            dtype=torch.float32,
        )

        # --- Categorical list fields ---
        cat_fields = {}
        for field in LIST_FIELDS:
            val = row[field] if field in row.index else ""
            ids = self.vocab_builder.encode_list(val, field)
            cat_fields[field] = torch.tensor(ids, dtype=torch.long)

        # --- Single-value categorical fields ---
        for field in SINGLE_CAT_FIELDS:
            val = row[field] if field in row.index else ""
            cat_fields[field] = torch.tensor(
                self.vocab_builder.encode_single(val, field), dtype=torch.long
            )

        label = torch.tensor(self.labels[idx], dtype=torch.long)
        return img, numeric, cat_fields, label


# =============================================================================
# YOUR CODE: Image Branch
# =============================================================================

class ConvBlock(nn.Module):
    """Conv2d → BatchNorm → ReLU → MaxPool2d(2)."""

    def __init__(self, in_ch, out_ch):
        super().__init__()
        self.block = nn.Sequential(
            nn.Conv2d(in_ch, out_ch, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(out_ch),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
        )

    def forward(self, x):
        return self.block(x)


class ImageBranch(nn.Module):
    """
    Takes a (batch, 3, H, W) poster tensor and produces a feature vector.

    4 convolutional blocks progressively halve spatial size:
        128 → 64 → 32 → 16 → 8
    Then global average pooling collapses spatial dims, followed by a
    dropout + linear projection to out_dim.
    """

    def __init__(self, out_dim=256, dropout=0.4):
        super().__init__()
        self.conv = nn.Sequential(
            ConvBlock(3,   32),   # 128 → 64
            ConvBlock(32,  64),   #  64 → 32
            ConvBlock(64,  128),  #  32 → 16
            ConvBlock(128, 256),  #  16 →  8
        )
        self.pool = nn.AdaptiveAvgPool2d(1)   # (batch, 256, 1, 1)
        self.head = nn.Sequential(
            nn.Flatten(),
            nn.Dropout(dropout),
            nn.Linear(256, out_dim),
            nn.ReLU(inplace=True),
        )

    def forward(self, x):
        return self.head(self.pool(self.conv(x)))


# =============================================================================
# YOUR CODE: Tabular Branch
# =============================================================================

class TabularBranch(nn.Module):
    """
    Two sub-branches merged into a single feature vector:

    Numeric sub-branch:
        standardised numeric features → FC(7→64) → ReLU → Dropout → FC(64→128) → ReLU

    Embedding sub-branch:
        For each LIST_FIELD: embed tokens → max-pool (ignoring PAD) → 32-dim vector
        For each SINGLE_CAT_FIELD: embed scalar → 32-dim vector
        Concatenate all → FC(total→128) → ReLU → Dropout

    Merge: concat(numeric_out, embed_out) → FC(256→out_dim) → ReLU
    """

    def __init__(self, vocab_sizes, out_dim=256, dropout=0.3):
        super().__init__()
        n_numeric = len(NUMERIC_COLS)

        # Numeric sub-branch
        self.numeric_net = nn.Sequential(
            nn.Linear(n_numeric, 64),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout),
            nn.Linear(64, 128),
            nn.ReLU(inplace=True),
        )

        # One embedding table per field (list + single-value)
        all_fields = LIST_FIELDS + SINGLE_CAT_FIELDS
        self.embeddings = nn.ModuleDict({
            field: nn.Embedding(vocab_sizes[field], EMBED_DIM, padding_idx=0)
            for field in all_fields
            if field in vocab_sizes
        })

        embed_total = len(self.embeddings) * EMBED_DIM
        self.embed_net = nn.Sequential(
            nn.Linear(embed_total, 128),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout),
        )

        # Merge sub-branches
        self.merge = nn.Sequential(
            nn.Linear(128 + 128, out_dim),
            nn.ReLU(inplace=True),
        )

    def _max_pool(self, emb, ids):
        """Max-pool token embeddings; padding_idx=0 guarantees PAD → zero vector."""
        pooled, _ = emb.max(dim=1)   # (B, E)
        return pooled

    def forward(self, numeric, cat_fields):
        # Numeric sub-branch
        num_out = self.numeric_net(numeric)

        # Embedding sub-branch
        pooled_vecs = []
        for field, emb_layer in self.embeddings.items():
            ids = cat_fields[field]
            if ids.dim() == 1:
                # Single-value field: embed scalar index → (B, E)
                pooled = emb_layer(ids)
            else:
                # List field: embed sequence → (B, L, E), then max-pool → (B, E)
                pooled = self._max_pool(emb_layer(ids), ids)
            pooled_vecs.append(pooled)

        embed_out = self.embed_net(torch.cat(pooled_vecs, dim=1))

        return self.merge(torch.cat([num_out, embed_out], dim=1))


# =============================================================================
# YOUR CODE: Fusion Head
# =============================================================================

class FusionHead(nn.Module):
    """
    Concatenates image and tabular feature vectors and predicts genre.
    Output: (batch, num_classes) logits (no softmax — use CrossEntropyLoss).
    """

    def __init__(self, image_dim, tabular_dim, num_classes=len(GENRES), dropout=0.4):
        super().__init__()
        fused = image_dim + tabular_dim
        self.net = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(fused, 256),
            nn.ReLU(inplace=True),
            nn.Dropout(0.3),
            nn.Linear(256, num_classes),
        )

    def forward(self, image_features, tabular_features):
        return self.net(torch.cat([image_features, tabular_features], dim=1))


# =============================================================================
# YOUR CODE: Full Model
# =============================================================================

class MultimodalGenreClassifier(nn.Module):
    """Wires ImageBranch, TabularBranch, and FusionHead together."""

    IMAGE_DIM   = 256
    TABULAR_DIM = 256

    def __init__(self, vocab_sizes):
        super().__init__()
        self.image_branch   = ImageBranch(out_dim=self.IMAGE_DIM)
        self.tabular_branch = TabularBranch(vocab_sizes, out_dim=self.TABULAR_DIM)
        self.fusion_head    = FusionHead(self.IMAGE_DIM, self.TABULAR_DIM)

    def forward(self, image, numeric, cat_fields):
        img_feat = self.image_branch(image)
        tab_feat = self.tabular_branch(numeric, cat_fields)
        return self.fusion_head(img_feat, tab_feat)


# =============================================================================
# Training utilities
# =============================================================================

def _accuracy(logits, labels):
    return (logits.argmax(dim=1) == labels).float().mean().item()


def collate_fn(batch):
    """Stack a list of (img, numeric, cat_fields, label) tuples."""
    imgs, numerics, cat_list, labels = zip(*batch)
    imgs     = torch.stack(imgs)
    numerics = torch.stack(numerics)
    labels   = torch.stack(labels)
    cat_fields = {k: torch.stack([d[k] for d in cat_list]) for k in cat_list[0]}
    return imgs, numerics, cat_fields, labels


def train_one_epoch(model, loader, criterion, optimizer, device):
    model.train()
    total_loss, total_acc, n = 0.0, 0.0, 0
    for imgs, numeric, cat_fields, labels in tqdm(loader, leave=False, desc="train"):
        imgs       = imgs.to(device)
        numeric    = numeric.to(device)
        cat_fields = {k: v.to(device) for k, v in cat_fields.items()}
        labels     = labels.to(device)

        optimizer.zero_grad()
        logits = model(imgs, numeric, cat_fields)
        loss   = criterion(logits, labels)
        loss.backward()
        optimizer.step()

        bs = labels.size(0)
        total_loss += loss.item() * bs
        total_acc  += _accuracy(logits, labels) * bs
        n += bs
    return total_loss / n, total_acc / n


@torch.no_grad()
def evaluate(model, loader, criterion, device):
    model.eval()
    total_loss, total_acc, n = 0.0, 0.0, 0
    for imgs, numeric, cat_fields, labels in loader:
        imgs       = imgs.to(device)
        numeric    = numeric.to(device)
        cat_fields = {k: v.to(device) for k, v in cat_fields.items()}
        labels     = labels.to(device)

        logits = model(imgs, numeric, cat_fields)
        loss   = criterion(logits, labels)

        bs = labels.size(0)
        total_loss += loss.item() * bs
        total_acc  += _accuracy(logits, labels) * bs
        n += bs
    return total_loss / n, total_acc / n


@torch.no_grad()
def per_class_accuracy(model, loader, device):
    model.eval()
    correct = Counter()
    total   = Counter()
    for imgs, numeric, cat_fields, labels in loader:
        imgs       = imgs.to(device)
        numeric    = numeric.to(device)
        cat_fields = {k: v.to(device) for k, v in cat_fields.items()}
        preds      = model(imgs, numeric, cat_fields).argmax(dim=1).cpu()
        for pred, label in zip(preds, labels):
            total[label.item()]   += 1
            correct[label.item()] += int(pred == label)
    return {GENRES[i]: correct[i] / total[i] for i in range(len(GENRES)) if total[i] > 0}


# =============================================================================
# Main
# =============================================================================

def main():
    CKPT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Device : {DEVICE}")
    print(f"Data   : {DATA_DIR}")

    # --- Load manifests ---
    train_df = pd.read_csv(DATA_DIR / "train_manifest.csv")
    val_df   = pd.read_csv(DATA_DIR / "val_manifest.csv")
    test_df  = pd.read_csv(DATA_DIR / "test_manifest.csv")
    print(f"Train: {len(train_df):,}  Val: {len(val_df):,}  Test: {len(test_df):,}")

    # --- Fit preprocessors on training data ONLY ---
    vocab_builder  = VocabBuilder(top_n=TOP_N_VOCAB).fit(train_df)
    numeric_scaler = NumericScaler().fit(train_df)

    # --- Image transforms ---
    train_transform = transforms.Compose([
        transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
        transforms.RandomHorizontalFlip(),
        transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.1),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    eval_transform = transforms.Compose([
        transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    # --- Datasets & DataLoaders ---
    train_ds = MoviePosterDataset(train_df, IMAGE_DIR, vocab_builder, numeric_scaler, train_transform)
    val_ds   = MoviePosterDataset(val_df,   IMAGE_DIR, vocab_builder, numeric_scaler, eval_transform)
    test_ds  = MoviePosterDataset(test_df,  IMAGE_DIR, vocab_builder, numeric_scaler, eval_transform)

    loader_kw = dict(collate_fn=collate_fn, num_workers=2, pin_memory=True)
    train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True,  **loader_kw)
    val_loader   = DataLoader(val_ds,   batch_size=BATCH_SIZE, shuffle=False, **loader_kw)
    test_loader  = DataLoader(test_ds,  batch_size=BATCH_SIZE, shuffle=False, **loader_kw)

    # --- Model ---
    model = MultimodalGenreClassifier(vocab_sizes=vocab_builder.sizes).to(DEVICE)
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"Trainable parameters: {trainable:,}")

    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=LR, weight_decay=WEIGHT_DECAY)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode="max", patience=3, factor=0.5
    )

    best_val_acc   = 0.0
    best_ckpt_path = CKPT_DIR / "best_movie_genre_model.pth"

    # --- Training loop ---
    for epoch in range(1, NUM_EPOCHS + 1):
        train_loss, train_acc = train_one_epoch(model, train_loader, criterion, optimizer, DEVICE)
        val_loss,   val_acc   = evaluate(model, val_loader, criterion, DEVICE)
        scheduler.step(val_acc)

        print(
            f"Epoch {epoch:3d}/{NUM_EPOCHS}  "
            f"train_loss={train_loss:.4f}  train_acc={train_acc:.4f}  "
            f"val_loss={val_loss:.4f}  val_acc={val_acc:.4f}"
        )

        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save(
                {
                    "epoch":                epoch,
                    "model_state_dict":     model.state_dict(),
                    "optimizer_state_dict": optimizer.state_dict(),
                    "val_acc":              val_acc,
                },
                best_ckpt_path,
            )
            print(f"  ✓ Best model saved (val_acc={val_acc:.4f})")

    # --- Test evaluation ---
    print("\n--- Loading best checkpoint for test evaluation ---")
    ckpt = torch.load(best_ckpt_path, map_location=DEVICE)
    model.load_state_dict(ckpt["model_state_dict"])

    _, test_acc = evaluate(model, test_loader, criterion, DEVICE)
    print(f"Test accuracy (overall): {test_acc:.4f}")

    print("\nPer-class accuracy on test set:")
    for genre, acc in per_class_accuracy(model, test_loader, DEVICE).items():
        print(f"  {genre:<15} {acc:.4f}")


if __name__ == "__main__":
    main()
