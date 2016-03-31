Summary:	The official GitLab CI runner written in Go
Name:		gitlab-ci-multi-runner
Version:	1.1.0
Release:	0.1
License:	GPL v3
Group:		Development/Building
Source0:	https://gitlab.com/gitlab-org/gitlab-ci-multi-runner/repository/archive.tar.gz?ref=v%{version}&/%{name}-%{version}.tar.gz
# Source0-md5:	4145931bc59d40e32df6ee24e15a19d3
URL:		https://gitlab.com/gitlab-org/gitlab-ci-multi-runner
BuildRequires:	git-core
BuildRequires:	golang
Requires:	ca-certificates
Requires:	curl
Requires:	git-core
Requires:	tar
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
This is the official GitLab Runner written in Go. It runs tests and
sends the results to GitLab. GitLab CI is the open-source continuous
integration service included with GitLab that coordinates the testing.

%prep
%setup -qc
mv gitlab-ci-multi-runner-*/{.??*,*} .

install -d Godeps/_workspace/src/gitlab.com/gitlab-org
ln -s ../../../../.. Godeps/_workspace/src/gitlab.com/gitlab-org/gitlab-ci-multi-runner

%build
export GOPATH=$(pwd):$(pwd)/Godeps/_workspace

go build

%install
rm -rf $RPM_BUILD_ROOT

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc README.md CHANGELOG.md
