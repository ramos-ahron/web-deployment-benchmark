# infra

Owner: Nathan

Records the VMs and how they connect.

Planned contents:

- `vm-inventory.md`: role, flavor, vCPUs, RAM, disk, OS, and software versions for each VM.
- Notes on SSH access: who has access to which machine. Public keys only, never private keys.
- Results of the connectivity checks between VMs.
- MariaDB setup steps, including how the WordPress database and user were created. Do not include the password.

Aaron and the report depend on `vm-inventory.md`, so keep it current.

## Infrastructure documentation

- [VM inventory and verified configuration](vm-inventory.md)
- [Backup inventory and recovery status](backups.md)
- [Team handoff and comparison requirements](handoff.md)

Credentials, SSH private keys, application archives, and database dumps must remain outside this repository.
