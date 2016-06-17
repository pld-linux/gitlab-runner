# the revision for images
%define	revision	88fc806
Summary:	The official GitLab CI runner written in Go
Name:		gitlab-ci-multi-runner
Version:	1.1.3
Release:	1
License:	MIT
Group:		Development/Building
Source0:	https://gitlab.com/gitlab-org/gitlab-ci-multi-runner/repository/archive.tar.gz?ref=v%{version}&/%{name}-%{version}.tar.gz
# Source0-md5:	3ce0499c2ee0bca486dcdaf1bb01d2d1
Source1:	https://gitlab-ci-multi-runner-downloads.s3.amazonaws.com/master/docker/prebuilt.tar.gz
# Source1-md5:	d616dcc457a6ce69bed4af2ca08dfe0a
URL:		https://gitlab.com/gitlab-org/gitlab-ci-multi-runner
BuildRequires:	git-core
BuildRequires:	go-bindata >= 3.0.7-1.a0ff2567
BuildRequires:	golang
Requires:	ca-certificates
Requires:	curl
Requires:	git-core
Requires:	tar
Suggests:	docker >= 1.5.0
ExclusiveArch:	%{ix86} %{x8664} %{arm}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

# go stuff
%define _enable_debug_packages 0
%define gobuild(o:) go build -ldflags "${LDFLAGS:-} -B 0x$(head -c20 /dev/urandom|od -An -tx1|tr -d ' \\n')" -a -v -x %{?**};

%description
This is the official GitLab Runner written in Go. It runs tests and
sends the results to GitLab. GitLab CI is the open-source continuous
integration service included with GitLab that coordinates the testing.

%prep
%setup -qc
mv gitlab-ci-multi-runner-*/{.??*,*} .

install -d Godeps/_workspace/src/gitlab.com/gitlab-org
ln -s ../../../../.. Godeps/_workspace/src/gitlab.com/gitlab-org/gitlab-ci-multi-runner

mkdir -p out/docker
ln -s %{SOURCE1} out/docker/prebuilt.tar.gz
# touch, otherwise make rules would download it nevertheless
touch out/docker/prebuilt.tar.gz

# avoid docker being used even if executable found
cat <<'EOF' > docker
#!/bin/sh
echo >&2 "No docker"
exit 1
EOF
chmod a+rx docker

%build
# check that the revision is correct
tar xvf out/docker/prebuilt.tar.gz repositories
revision=$(sed -rne 's/.*"gitlab-runner-build":\{"([^"]+)":.*/\1/p' repositories)
test "$revision" = %{revision}

export GOPATH=$(pwd):$(pwd)/Godeps/_workspace
export PATH=$(pwd):$PATH

%{__make} docker
%{__make} version | tee version.txt

LDFLAGS="-X main.NAME gitlab-ci-multi-runner -X main.VERSION %{version} -X main.REVISION %{revision}"
%gobuild

# verify version match
./gitlab-ci-multi-runner-%{version} -v > v
grep 'version %{version} ' v

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_bindir}
install -p %{name}-%{version} $RPM_BUILD_ROOT%{_bindir}/%{name}

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc README.md CHANGELOG.md
%attr(755,root,root) %{_bindir}/gitlab-ci-multi-runner
