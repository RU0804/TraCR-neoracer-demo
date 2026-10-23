# GitHub publication and updates

The user created the public repository [RU0804/TraCR-neoracer-demo](https://github.com/RU0804/TraCR-neoracer-demo) and explicitly selected Public visibility. Preserve that setting. This workspace's origin is `https://github.com/RU0804/TraCR-neoracer-demo.git`. Source, validation records, screenshots and map-construction guidance have been uploaded; the first complete publication verified identical local and remote Git trees.

Version source files, small validation screenshots and documentation. Exclude Python environments, downloaded Unity projects, binaries, recordings and local calibration files. Review `git status --short` and `git diff --cached --stat` before committing. Keep local configuration in `configs/local*.json` and tokens in environment variables.

To obtain the repository on a development machine:

```bash
git clone https://github.com/RU0804/TraCR-neoracer-demo.git
cd TraCR-neoracer-demo
```

To update it from a machine with GitHub write authentication:

```bash
git pull --ff-only
# Commit reviewed and validated changes before pushing.
git push origin main
```

Do not force-push over an existing nonempty remote. This environment publishes through the connected GitHub file/Git-data APIs without a local gh login. The public repository can be fetched directly over HTTPS.

A source ZIP does not contain `.git`. Prefer `git clone`, or use the provided Git bundle to retain local history. Keep recordings in the ignored `recordings/` directory and check data provenance and authorization before publishing them separately.

The repository currently has no open-source LICENSE. Public visibility does not select a license on the project owner's behalf. AutoDRIVE models and other third-party assets are neither relicensed nor bundled.
