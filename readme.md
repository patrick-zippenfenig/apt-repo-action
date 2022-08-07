# Github pages APT repo

This action will create a single APT repo for a single dpkg file.

Forked from https://github.com/jrandiny/apt-repo-action and all git logic removed

## Inputs

### `repo_supported_arch`

**Required** Newline-delimited list of supported architecture

### `repo_supported_version`

**Required** Newline-delimited list of supported (linux) version

### `file`

**Required** .deb files to be included

### `file_target_version`

**Required** Version target of supplied .deb file

### `private_key`

**Required** GPG private key for signing APT repo

### `public_key`

GPG public key for APT repo

### `key_passphrase`

Passphrase of GPG private key

### `repo_folder`

Location of APT repo folder relative to root of Github pages. Defaults to `repo`

## Example usage

```yaml
uses: jrandiny/apt-repo-action@v1
with:
  arch: |
    amd64
    i386
  version: |
    bionic
    trusty
  file: my_program_bionic.deb
  file_target_version: bionic
  public_key: ${{ secrets.PUBLIC }}
  private_key: ${{ secrets.PRIVATE }}
  key_passphrase: ${{ secrets.SECRET }}
```