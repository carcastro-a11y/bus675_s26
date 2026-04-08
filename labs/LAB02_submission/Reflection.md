# Lab 2 Reflection

In this lab, both containers ran on your laptop. In production, the preprocessor would run in the warehouse datacenter and the inference API would run in Congo's main datacenter.

**How would the architecture and your `docker run` commands differ if these containers were actually running in separate datacenters?**

Consider:
- How would the preprocessor find the inference API?
- What about the shared volumes?
- What new challenges would arise?


## Your Reflection Below

The biggest change would be how the preprocessor finds the inference API. On my laptop, I used `host.docker.internal:8000` because both containers were running on the same machine. In a real two-datacenter setup, that trick doesn't work anymore, the preprocessor would need to hit the inference API's actual public IP address or domain name (something like `http://api.congo-main-dc.com:8000`). That means the `-e API_URL=...` flag in the `docker run` command for the preprocessor would point to a real internet address instead of a local host alias. You'd also want to add HTTPS and some form of API authentication, since the traffic would be crossing a public network rather than staying on one machine.

The shared volumes would also need a complete rethink. Right now, `~/incoming` and `~/logs` are just folders on my laptop that both containers happen to have access to through bind mounts — easy. But if the preprocessor is in a warehouse datacenter and the API is in a main datacenter, there's no shared filesystem to mount. You'd need to replace those volumes with something like an S3 bucket or an NFS share so both sides can read and write to the same storage. On top of that, network latency between datacenters would slow down every image upload, and you'd have to think about what happens when the connection drops mid-transfer. It really highlighted for me how much the "just mount a folder" approach hides the complexity of what a distributed system actually has to deal with.