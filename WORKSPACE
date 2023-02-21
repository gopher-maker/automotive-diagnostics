workspace(name = "automotive-diagnostics")

load(
    "@bazel_tools//tools/build_defs/repo:git.bzl",
    "git_repository",
    "new_git_repository",
)
load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

# Golang build rules.
# NOTE: Buildifier is written in Go and hence needs rules_go to be built. See
# https://github.com/bazelbuild/rules_go for the up to date setup instructions.
http_archive(
    name = "io_bazel_rules_go",
    sha256 = "d6b2513456fe2229811da7eb67a444be7785f5323c6708b38d851d2b51e54d83",
    urls = [
        "https://mirror.bazel.build/github.com/bazelbuild/rules_go/releases/download/v0.30.0/rules_go-v0.30.0.zip",
        "https://github.com/bazelbuild/rules_go/releases/download/v0.30.0/rules_go-v0.30.0.zip",
    ],
)

load("@io_bazel_rules_go//go:deps.bzl", "go_rules_dependencies")

go_rules_dependencies()

load("@io_bazel_rules_go//go:deps.bzl", "go_register_toolchains")

go_register_toolchains(version = "1.17.2")

# Bazel team's build file generator for Bazel projects.
http_archive(
    name = "bazel_gazelle",
    sha256 = "de69a09dc70417580aabf20a28619bb3ef60d038470c7cf8442fafcf627c21cb",
    urls = [
        "https://mirror.bazel.build/github.com/bazelbuild/bazel-gazelle/releases/download/v0.24.0/bazel-gazelle-v0.24.0.tar.gz",
        "https://github.com/bazelbuild/bazel-gazelle/releases/download/v0.24.0/bazel-gazelle-v0.24.0.tar.gz",
    ],
)

load("@bazel_gazelle//:deps.bzl", "gazelle_dependencies")

gazelle_dependencies(go_repository_default_config = "@//:WORKSPACE")

# Google's Protocol Buffers (aka protobuf) for structured data serialization.
http_archive(
    name = "com_google_protobuf",
    sha256 = "25680843adf0c3302648d35f744e38cc3b6b05a6c77a927de5aea3e1c2e36106",
    strip_prefix = "protobuf-3.19.4",
    urls = ["https://github.com/protocolbuffers/protobuf/archive/refs/tags/v3.19.4.zip"],
)

load("@com_google_protobuf//:protobuf_deps.bzl", "protobuf_deps")

protobuf_deps()

# Bazel team's developer tools for formatting and managing BUILD.bazel files.
http_archive(
    name = "com_github_bazelbuild_buildtools",
    sha256 = "e9dc2d36e645e4c76759a135d64b0647fc9bd3e2c78ad01adbb3c4e361bb1862",
    strip_prefix = "buildtools-5.0.0",
    url = "https://github.com/bazelbuild/buildtools/archive/refs/tags/5.0.0.zip",
)

# Utility for creating self-contained python executables.
http_archive(
    name = "subpar",
    sha256 = "8876244a984d75f28b1c64d711b6e5dfab5f992a3b741480e63cfc5e26acba93",
    strip_prefix = "subpar-2.0.0",
    urls = ["https://github.com/google/subpar/archive/refs/tags/2.0.0.zip"],
)

# Bazel team's python rules.
http_archive(
    name = "rules_python",
    sha256 = "a30abdfc7126d497a7698c29c46ea9901c6392d6ed315171a6df5ce433aa4502",
    strip_prefix = "rules_python-0.6.0",
    url = "https://github.com/bazelbuild/rules_python/archive/0.6.0.tar.gz",
)

load("@rules_python//python:pip.bzl", "pip_parse")

# Python requirements.txt rules.
pip_parse(
    name = "py_automotive_diagnostics",
    requirements_lock = "//build:requirements.txt",
)

load("@py_automotive_diagnostics//:requirements.bzl", "install_deps")

install_deps()
