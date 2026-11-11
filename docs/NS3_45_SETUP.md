# NS-3.45 Setup and Compatibility Rules

## 1. Verify the installed source before running commands

The project is frozen to **NS-3.45** because the college material identifies that release. At the workspace root, inspect:

- `VERSION` if present;
- `RELEASE_NOTES`;
- `README.md`;
- the `ns3` wrapper;
- build configuration and any local scripts.

Run `./ns3 --help` (or inspect its help if platform shell differs). Do not assume the workspace actually contains 3.45 until verified.

## 2. Important build-system correction

NS-3.45 uses the CMake-backed `./ns3` wrapper. The official 3.45 guide's initial workflow is:

```bash
./ns3 configure --enable-examples --enable-tests
./ns3 build
```

A scratch program is typically run using a command shaped like:

```bash
./ns3 run "scratch/manet-aat --protocol=AODV --numNodes=10 --nodeSpeed=10"
```

Verify the exact argument quoting/runner syntax via `./ns3 --help` and local examples. **Do not run `./waf` for NS-3.45.** Older course PDFs/slides may contain Waf commands from older releases; do not combine the two build systems.

Official release-specific references:

- Installation: https://www2.nsnam.org/docs/release/3.45/installation/singlehtml/index.html
- Tutorial: https://www.nsnam.org/docs/release/3.45/tutorial/html/quick-start.html
- Model library: https://www.nsnam.org/docs/release/3.45/models/ns-3-model-library.pdf

## 3. Platform approach

- Linux is the primary-supported NS-3 platform. If the existing Windows-native setup is already working, do not switch platforms gratuitously.
- If native Windows build or GUI requirements block progress, inspect whether WSL2/Ubuntu is available and recommend it as a controlled alternative. Do not install/enable WSL or alter system settings without the user's approval.
- Keep Cursor's workspace on the same filesystem/context where the commands run. Record whether paths are Windows, WSL or Linux paths.
- Do not assume NetAnim's GUI is installed merely because the NS-3 module can emit animation XML.

## 4. Modules/features to confirm

Confirm support/headers for:

- core, network, internet, applications;
- wifi, mobility;
- aodv, dsdv;
- flow-monitor;
- netanim module/`AnimationInterface`.

The official NS-3.45 quick start lists these modules among standard configured modules, but the actual configured local build is authoritative.

## 5. Reuse the local reference example

Inspect these in the installed 3.45 tree:

- `examples/routing/manet-routing-compare.cc`;
- relevant protocol examples and headers;
- `src/aodv`, `src/dsdv`, `src/flow-monitor`, `src/netanim` API headers if needed.

Use the official MANET comparison example as a reference for the known-good Wi-Fi ad-hoc/mobility/protocol setup. Adapt to a **new** `scratch/manet-aat.cc` file. Preserve required license/attribution if copying substantial portions. Do not edit the original example or NS-3 core modules.

## 6. No destructive changes

Do not delete `build/`, run `git reset --hard`, reinstall NS-3, or change releases to solve an ordinary compile error. First read the error, check the installed API and fix the new project code. Ask permission before an irreversible operation.
