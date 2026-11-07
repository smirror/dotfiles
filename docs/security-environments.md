# Optional security toolbox

The intended category is the tools distributed with Kali Linux and Parrot OS.
They are currently used infrequently: keep them outside the host/global tool
set and make a reviewed isolated toolbox available when needed. Do not install
all of these tools through host apt, Brew, npm or pip.

| Need | Candidate environment | What must be prepared |
| --- | --- | --- |
| A ready CLI toolbox | Official `parrotsec/security` image | Review the included tools, architecture and final image digest |
| A selected Kali CLI tool set | An image based on official `kalilinux/kali-rolling` | Build the selected tools once on the other validation PC and record the resulting image digest/package manifest |
| Desktop tools, hardware access or networking that the container cannot provide | A dedicated Kali/Parrot VM | Choose a compatible distribution image/version, verify it and keep host integrations explicit |

Kali's standard Docker base does not include the default tool metapackage.
Parrot's security image includes CLI tool metapackages but deliberately omits
desktop applications. See [Kali's official Docker guide](https://www.kali.org/docs/containers/using-kali-docker-images/)
and [Parrot's official image catalog](https://parrotsec.org/docs/containers/parrot-on-docker/).

For quick future use, the desired operation is to start an already prepared,
pinned image. Do not run apt update/install on every launch: the result would
depend on the repository state at that time. A base-image digest alone does not
pin packages subsequently fetched during an image build. Record the finished
tool image digest and package versions; exact rebuilds also need a suitable
package-repository snapshot. Rolling distributions use an approved dated image
snapshot rather than a fictitious permanent stable-release number.

The first image retrieval still takes time; caching it ahead of use is optional
on the other PC. No image pull, build, launch, prefetch or VM installation is
authorized on the current PC by this definition. No concrete image digest has
been enrolled or tested yet, so this is not a ready-to-run launcher. The next
implementation step is to choose one default toolbox, fix its final image and
prepare a small explicit launcher on the validation PC.

Do not mount the home directory or Docker socket. Start with no mounts and
only explicitly required target/output paths and networking. Do not enable host
networking, privileged mode or device access as a generic workaround; choose an
appropriate VM when needed. Running a toolbox is separate from authorizing any
network test or target. Existing host applications are not removed by this plan.
