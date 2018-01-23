Summary:	The official GitLab CI runner written in Go
Name:		gitlab-runner
Version:	10.4.0
Release:	1
License:	MIT
Group:		Development/Building
Source0:	https://gitlab.com/gitlab-org/gitlab-runner/repository/archive.tar.gz?ref=v%{version}&/%{name}-%{version}.tar.gz
# Source0-md5:	7e861abe57252a35136d09a060076c77
Source3:	%{name}.init
Source4:	%{name}.sysconfig
Source5:	%{name}.service
Patch0:		nodim_gz.patch
Patch1:		branch-preserver.patch
URL:		https://gitlab.com/gitlab-org/gitlab-runner
BuildRequires:	git-core
BuildRequires:	golang >= 1.6
BuildRequires:	rpmbuild(macros) >= 1.647
Requires(post,preun):	/sbin/chkconfig
Requires(post,preun,postun):	systemd-units >= 38
Requires(postun):	/usr/sbin/groupdel
Requires(postun):	/usr/sbin/userdel
Requires(pre):	/bin/id
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
Requires:	bash
Requires:	ca-certificates
Requires:	git-core
Requires:	rc-scripts
Requires:	systemd-units >= 0.38
Requires:	tar
Suggests:	docker >= 1.8
Suggests:	gitlab-runner-image-arm
Suggests:	gitlab-runner-image-x86_64
Provides:	group(gitlab-runner)
Provides:	user(gitlab-runner)
Obsoletes:	gitlab-ci-multi-runner < 10.0
ExclusiveArch:	%{ix86} %{x8664} %{arm}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

# go stuff
%define _enable_debug_packages 0
%define gobuild(o:) go build -ldflags "${LDFLAGS:-} -B 0x$(head -c20 /dev/urandom|od -An -tx1|tr -d ' \\n')" -a -v %{?debug:-x} %{?**};
%define import_path	gitlab.com/gitlab-org/gitlab-runner

%description
This is the official GitLab Runner written in Go. It runs tests and
sends the results to GitLab. GitLab CI is the open-source continuous
integration service included with GitLab that coordinates the testing.

%prep
%setup -qc

# for doc
mv gitlab-runner-*/*.md .

# don't you love go?
install -d src/$(dirname %{import_path})
mv gitlab-runner-* src/%{import_path}
cd src/%{import_path}

%patch0 -p5
%patch1 -p1

# avoid docker being used even if executable found
cat <<'EOF' > docker
#!/bin/sh
echo >&2 "No docker"
exit 1
EOF
chmod a+rx docker

%build
export GOPATH=$(pwd)
cd src/%{import_path}
export PATH=$(pwd):$PATH

%{__make} version | tee version.txt

CN=gitlab.com/gitlab-org/gitlab-runner/common
LDFLAGS="-X $CN.NAME=gitlab-runner -X $CN.VERSION=%{version} -X $CN.REVISION=%{version}"
%gobuild

# verify that version matches
./gitlab-runner -v > v
v=$(awk '$1 == "Version:" {print $2}' v)
test "$v" = "%{version}"

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sysconfdir}/gitlab-runner,%{_bindir},/etc/{rc.d/init.d,sysconfig},%{systemdunitdir},/var/lib/gitlab-runner/.gitlab-runner}

install -p src/%{import_path}/%{name} $RPM_BUILD_ROOT%{_bindir}/gitlab-runner
install -p %{SOURCE3} $RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}
cp -p %{SOURCE4} $RPM_BUILD_ROOT/etc/sysconfig/%{name}
cp -p %{SOURCE5} $RPM_BUILD_ROOT%{systemdunitdir}

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%groupadd -g 330 gitlab-runner
%useradd -u 330 -d /var/lib/gitlab-runner -g gitlab-runner -c "GitLab Runner" gitlab-runner

%postun
if [ "$1" = "0" ]; then
	%userremove gitlab-runner
	%groupremove gitlab-runner
fi
%systemd_reload

%post
/sbin/chkconfig --add %{name}
%service %{name} restart
%systemd_post %{name}.service

%preun
if [ "$1" = "0" ]; then
	%service -q %{name} stop
	/sbin/chkconfig --del %{name}
fi
%systemd_preun %{name}.service

%files
%defattr(644,root,root,755)
%doc README.md CHANGELOG.md
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/gitlab-runner
%attr(754,root,root) /etc/rc.d/init.d/gitlab-runner
%dir %attr(750,root,root) %{_sysconfdir}/gitlab-runner
%attr(755,root,root) %{_bindir}/gitlab-runner
%{systemdunitdir}/gitlab-runner.service
%dir %attr(750,gitlab-runner,gitlab-runner) /var/lib/gitlab-runner
%dir %attr(750,gitlab-runner,gitlab-runner) /var/lib/gitlab-runner/.gitlab-runner
