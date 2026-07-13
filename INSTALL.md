# Installation from a release

Each tagged release contains self-contained .NET 10 command-line packages for Windows, Linux and macOS on x64 and ARM64. Select the archive matching the operating system and architecture, extract it, and verify that the executable reports the release version and passes its built-in self-test. A separate .NET installation is not required.

The release also contains a Python wheel and source distribution. Install the wheel in a fresh virtual environment and confirm that `metastable_suite.__version__` matches the release version.

Two multi-architecture OCI images are published in GitHub Container Registry: the platform CLI and the scientific worker. Stable releases additionally update their `latest` tags; prereleases never do.

Every release includes SHA-256 checksums and SPDX JSON software bills of materials. GitHub attestations associate the binary archives, Python packages and OCI image digests with the repository release workflow. Verify checksums and attestations before using downloaded artifacts on laboratory systems.

The root `VERSION` file is authoritative. `CITATION.cff`, Python package metadata, .NET assembly metadata, OCI labels and the Git tag are validated against it before publication.
