%global pypi_name manila-ui
%global mod_name manila_ui

# tests are disabled by default
%bcond_with tests

%{!?upstream_version: %global upstream_version %{version}%{?milestone}}

Name:           openstack-%{pypi_name}
Version:        2.5.1
Release:        1%{?dist}
Summary:        Manila Management Dashboard

License:        ASL 2.0
URL:            http://www.openstack.org/
Source0:        https://tarballs.openstack.org/%{pypi_name}/%{pypi_name}-%{version}.tar.gz
BuildArch:      noarch
 
BuildRequires:  python2-devel
BuildRequires:  python-pbr
BuildRequires:  python-sphinx
BuildRequires:  python-oslo-sphinx

%if 0%{with tests}
# test requirements
BuildRequires:  openstack-dashboard
BuildRequires:  python-hacking
BuildRequires:  python-django-horizon
BuildRequires:  python-django-nose
BuildRequires:  python-django-openstack-auth
BuildRequires:  python-manilaclient
BuildRequires:  python-mock
BuildRequires:  python-mox
BuildRequires:  python-subunit
BuildRequires:  python-testrepository
BuildRequires:  python-testscenarios
BuildRequires:  python-testtools
%endif

Requires: python-babel
Requires: python-django
Requires: python-django-compressor
Requires: python-django-horizon
Requires: python-django-openstack-auth
Requires: python-iso8601
Requires: python-keystoneclient
Requires: python-manilaclient
Requires: python-neutronclient
Requires: python-novaclient
Requires: python-pbr

%description
Manila Management Dashboard


%prep
%setup -q -n %{pypi_name}-%{upstream_version}
# Remove bundled egg-info
rm -rf %{pypi_name}.egg-info

rm test-requirements.txt

%build
%{__python2} setup.py build

# generate html docs 
sphinx-build doc/source html
# remove the sphinx-build leftovers
rm -rf html/.{doctrees,buildinfo}

for lib in %{mod_name}/dashboards/project/*.py; do
  sed '1{\@^#!/usr/bin/env python@d}' $lib > $lib.new &&
  touch -r $lib $lib.new &&
  mv $lib.new $lib
done


%install
%{__python2} setup.py install --skip-build --root %{buildroot}

# Move config to horizon
mkdir -p  %{buildroot}%{_sysconfdir}/openstack-dashboard/enabled
mkdir -p  %{buildroot}%{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled
mv manila_ui/enabled/_90_manila_admin_shares.py %{buildroot}%{_sysconfdir}/openstack-dashboard/enabled/_90_manila_admin_shares.py
mv manila_ui/enabled/_90_manila_project_shares.py %{buildroot}%{_sysconfdir}/openstack-dashboard/enabled/_90_manila_project_shares.py
ln -s %{_sysconfdir}/openstack-dashboard/enabled/_90_manila_admin_shares.py %{buildroot}%{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled/_90_manila_admin_shares.py
ln -s %{_sysconfdir}/openstack-dashboard/enabled/_90_manila_project_shares.py %{buildroot}%{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled/_90_manila_project_shares.py


%check
%if 0%{with tests}
PYTHONPATH=/usr/share/openstack-dashboard/ ./run_tests.sh -N -P
%endif


%files
%doc html README.rst doc/source/readme.rst
%license LICENSE
%{python2_sitelib}/%{mod_name}
%{python2_sitelib}/manila_ui-*-py?.?.egg-info
%{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled/_90_manila_admin_shares.py*
%{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled/_90_manila_project_shares.py*
%{_sysconfdir}/openstack-dashboard/enabled/_90_manila_admin_shares.py*
%{_sysconfdir}/openstack-dashboard/enabled/_90_manila_project_shares.py*


%changelog
* Tue Oct 04 2016 Alfredo Moralejo <amoralej@redhat.com> 2.5.1-1
- Update to 2.5.1

* Thu Sep 15 2016 Haikel Guemar <hguemar@fedoraproject.org> 2.5.0-1
- Update to 2.5.0


