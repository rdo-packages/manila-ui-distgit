%global pypi_name manila-ui
%global mod_name manila_ui

# tests are disabled by default
%bcond_with tests

%{!?upstream_version: %global upstream_version %{version}%{?milestone}}

Name:           openstack-%{pypi_name}
Version:        2.13.0
Release:        2%{?dist}
Summary:        Manila Management Dashboard

License:        ASL 2.0
URL:            http://www.openstack.org/
Source0:        https://tarballs.openstack.org/%{pypi_name}/%{pypi_name}-%{upstream_version}.tar.gz
BuildArch:      noarch

BuildRequires:  python2-devel
BuildRequires:  python2-pbr
BuildRequires:  python2-sphinx
BuildRequires:  python2-openstackdocstheme
BuildRequires:  git
BuildRequires:  openstack-macros

%if 0%{with tests}
# test requirements
BuildRequires:  openstack-dashboard >= 1:13.0.0
BuildRequires:  python2-hacking
BuildRequires:  python2-django-nose
BuildRequires:  python2-manilaclient
BuildRequires:  python2-neutronclient
BuildRequires:  python2-mock
BuildRequires:  python2-mox
BuildRequires:  python2-subunit
BuildRequires:  python2-testrepository
BuildRequires:  python2-testscenarios
BuildRequires:  python2-testtools
%endif

Requires: openstack-dashboard >= 1:13.0.0
Requires: python2-babel
Requires: python2-django
Requires: python2-django-compressor
Requires: python2-iso8601
Requires: python2-manilaclient >= 1.16.0
Requires: python2-pbr
Requires: python2-oslo-utils >= 3.33.0
Requires: python2-six
Requires: python2-keystoneclient >= 1:3.8.0


%description
Manila Management Dashboard


%prep
%autosetup -n %{pypi_name}-%{upstream_version} -S git
# Remove bundled egg-info
rm -rf %{pypi_name}.egg-info

%py_req_cleanup

%build
%{__python2} setup.py build

# generate html docs 
%{__python2} setup.py build_sphinx -b html
# remove the sphinx-build leftovers
rm -fr doc/build/html/.doctrees doc/build/html/.buildinfo

for lib in %{mod_name}/dashboards/project/*.py; do
  sed '1{\@^#!/usr/bin/env python@d}' $lib > $lib.new &&
  touch -r $lib $lib.new &&
  mv $lib.new $lib
done


%install
%{__python2} setup.py install --skip-build --root %{buildroot}

# Move config to horizon
mkdir -p  %{buildroot}%{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled
mkdir -p  %{buildroot}%{_datadir}/openstack-dashboard/openstack_dashboard/local/local_settings.d
mv manila_ui/local/enabled/_80_manila_*.py %{buildroot}%{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled/
mv manila_ui/local/enabled/_90*_manila_*.py %{buildroot}%{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled/
mv manila_ui/local/local_settings.d/_90_manila_*.py %{buildroot}%{_datadir}/openstack-dashboard/openstack_dashboard/local/local_settings.d/


%check
%if 0%{with tests}
PYTHONPATH=/usr/share/openstack-dashboard/ ./run_tests.sh -N -P
%endif


%files
%doc doc/build/html README.rst
%license LICENSE
%{python2_sitelib}/%{mod_name}
%{python2_sitelib}/manila_ui-*-py?.?.egg-info
%{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled/_80_manila_*.py*
%{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled/_90*_manila_*.py*
%{_datadir}/openstack-dashboard/openstack_dashboard/local/local_settings.d/_90_manila_*.py*


%changelog
* Tue Apr 17 2018 Victoria Martinez de la Cruz <vimartin@redhat.com> 2.13.0-2
- Add configs for manila-ui under enabled

* Sat Feb 17 2018 RDO <dev@lists.rdoproject.org> 2.13.0-1
- Update to 2.13.0

