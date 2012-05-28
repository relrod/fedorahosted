Name:           fedorahosted
Version:        0.0.1
Release:        1%{?dist}
Summary:        Fedora Hosted request automation

Group:          Applications/Internet
License:        GPLv2+
URL:            https://fedorahosted.org/
Source0:        https://fedorahosted.org/releases/f/e/fedorahosted/%{name}-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root
BuildArch:      noarch
BuildRequires:  python-setuptools
BuildRequires:  python-setuptools-devel
BuildRequires:  python-devel
Requires:       python-fedora
Requires:       python-flask
Requires:       python-flask-sqlalchemy
Requires:       python-flask-wtf
Requires:       python-sqlalchemy
Requires:       python-wtforms

%description
Stores, manages, and processes Fedora Hosted requests.

%package cli
Summary:        CLI to 'fedorahosted' to create or process requests

%description cli
Provides a CLI to 'fedorahosted' which allows administrators to process new
hosted requests, and users to create new requests alternatively to using the
flask web app.

%prep
%setup -q -n %{name}-%{version}

%build
%{__python} setup.py build

%install
rm -rf %{buildroot}
%{__python} setup.py install --skip-build --root %{buildroot}

mkdir -p %{buildroot}/%{_sbindir} %{buildroot}/%{_sysconfdir}/%{name}
install -m 640 etc/fedorahosted_config.py.dist \
  %{buildroot}%{_sysconfdir}/%{name}/fedorahosted_config.py

install -m 640 etc/cli.conf.dist %{buildroot}%{_sysconfdir}/%{name}/cli.conf

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
%config(noreplace) %{_sysconfdir}/%{name}/fedorahosted_config.*
%{python_sitelib}/*

%files cli
%{_bindir}/fedorahosted
%config(noreplace) %{_sysconfdir}/%{name}/cli.conf

%changelog
* Mon May 28 2012 Ricky Elrod <codeblock@fedoraproject.org> - 0.0.1-1
- Initial build.
