# Macros for py2/py3 compatibility
%if 0%{?fedora} || 0%{?rhel} > 7
%global pyver %{python3_pkgversion}
%else
%global pyver 2
%endif
%global pyver_bin python%{pyver}
%global pyver_sitelib %python%{pyver}_sitelib
%global pyver_install %py%{pyver}_install
%global pyver_build %py%{pyver}_build
# End of macros for py2/py3 compatibility
%global pypi_name manila-ui
%global mod_name manila_ui

# tests are disabled by default
%bcond_with tests

%{!?upstream_version: %global upstream_version %{version}%{?milestone}}

Name:           openstack-%{pypi_name}
Version:        XXX
Release:        XXX
Summary:        Manila Management Dashboard

License:        ASL 2.0
URL:            http://www.openstack.org/
Source0:        https://tarballs.openstack.org/%{pypi_name}/%{pypi_name}-%{upstream_version}.tar.gz
BuildArch:      noarch

BuildRequires:  python%{pyver}-devel
BuildRequires:  python%{pyver}-pbr
BuildRequires:  python%{pyver}-sphinx
BuildRequires:  python%{pyver}-openstackdocstheme
BuildRequires:  git
BuildRequires:  openstack-macros

%if 0%{with tests}
# test requirements
BuildRequires:  openstack-dashboard >= 1:14.0.0
BuildRequires:  python%{pyver}-hacking
BuildRequires:  python%{pyver}-django-nose
BuildRequires:  python%{pyver}-manilaclient
BuildRequires:  python%{pyver}-neutronclient
BuildRequires:  python%{pyver}-mock
BuildRequires:  python%{pyver}-mox
BuildRequires:  python%{pyver}-subunit
BuildRequires:  python%{pyver}-testrepository
BuildRequires:  python%{pyver}-testscenarios
BuildRequires:  python%{pyver}-testtools
%endif

Requires: openstack-dashboard >= 1:14.0.0
Requires: python%{pyver}-babel
Requires: python%{pyver}-django
Requires: python%{pyver}-django-compressor
Requires: python%{pyver}-iso8601
Requires: python%{pyver}-manilaclient >= 1.16.0
Requires: python%{pyver}-pbr
Requires: python%{pyver}-oslo-utils >= 3.33.0
Requires: python%{pyver}-six
Requires: python%{pyver}-keystoneclient >= 1:3.8.0


%description
Manila Management Dashboard


%prep
%autosetup -n %{pypi_name}-%{upstream_version} -S git
# Remove bundled egg-info
rm -rf %{pypi_name}.egg-info

%py_req_cleanup

%build
%{pyver_build}

# generate html docs
%{pyver_bin} setup.py build_sphinx -b html
# remove the sphinx-build-%{pyver} leftovers
rm -fr doc/build/html/.doctrees doc/build/html/.buildinfo

for lib in %{mod_name}/dashboards/project/*.py; do
  sed '1{\@^#!/usr/bin/env python@d}' $lib > $lib.new &&
  touch -r $lib $lib.new &&
  mv $lib.new $lib
done


%install
%{pyver_install}

# Move config to horizon
mkdir -p  %{buildroot}%{_sysconfdir}/openstack-dashboard/enabled
mkdir -p  %{buildroot}%{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled
mkdir -p  %{buildroot}%{_sysconfdir}/openstack-dashboard/local_settings.d
mkdir -p  %{buildroot}%{_datadir}/openstack-dashboard/openstack_dashboard/local/local_settings.d

# enabled allows toggling of panels and plugins
pushd .
cd %{buildroot}%{pyver_sitelib}/%{mod_name}/local/enabled
for f in _{80,90*}_manila_*.py*; do
    install -p -D -m 640 ${f} %{buildroot}%{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled/$(f)
done
popd
for f in %{buildroot}%{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled/_{80,90*}_manila_*.py*; do
    filename=`basename $f`
    ln -s %{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled/${filename} \
        %{buildroot}%{_sysconfdir}/openstack-dashboard/enabled/${filename}
done

# local_settings.d allows overriding of settings
pushd .
cd %{buildroot}%{pyver_sitelib}/%{mod_name}/local/local_settings.d
for f in _90_manila_*.py*; do
    install -p -D -m 640 ${f} %{buildroot}%{_datadir}/openstack-dashboard/openstack_dashboard/local/local_settings.d/$(f)
done
popd
for f in %{buildroot}%{_datadir}/openstack-dashboard/openstack_dashboard/local/local_settings.d/_90_manila_*.py*; do
    filename=`basename $f`
    ln -s %{_datadir}/openstack-dashboard/openstack_dashboard/local/local_settings.d/${filename} \
        %{buildroot}%{_sysconfdir}/openstack-dashboard/local_settings.d/${filename}
done

%check
%if 0%{with tests}
PYTHONPATH=/usr/share/openstack-dashboard/ ./run_tests.sh -N -P
%endif


%files
%doc doc/build/html README.rst
%license LICENSE
%{pyver_sitelib}/%{mod_name}
%{pyver_sitelib}/manila_ui-*-py?.?.egg-info
%{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled/_80_manila_*.py*
%{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled/_90*_manila_*.py*
%{_datadir}/openstack-dashboard/openstack_dashboard/local/local_settings.d/_90_manila_*.py*
%{_sysconfdir}/openstack-dashboard/enabled/_80_manila_*.py*
%{_sysconfdir}/openstack-dashboard/enabled/_90*_manila_*.py*
%{_sysconfdir}/openstack-dashboard/local_settings.d/_90_manila_*.py*

%changelog
# REMOVEME: error caused by commit http://git.openstack.org/cgit/openstack/manila-ui/commit/?id=82d991d2faa3e1a343c31cc52e82995eb3eedc27
