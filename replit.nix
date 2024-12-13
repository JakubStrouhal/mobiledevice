{pkgs}: {
  deps = [
    pkgs.dotnet-sdk
    pkgs.postgresql
    pkgs.openssl
  ];
}
