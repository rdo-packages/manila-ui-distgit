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

# RDO
%global rhosp 0

%global with_doc 1
# tests are disabled by default
%bcond_with tests

%{!?upstream_version: %global upstream_version %{version}%{?milestone}}

Name:           openstack-%{pypi_name}
Version:        2.19.1
Release:        1%{?dist}
Summary:        Manila Management Dashboard

License:        ASL 2.0
URL:            http://www.openstack.org/
Source0:        https://tarballs.openstack.org/%{pypi_name}/%{pypi_name}-%{upstream_version}.tar.gz
BuildArch:      noarch

BuildRequires:  python%{pyver}-devel
BuildRequires:  python%{pyver}-pbr
%if 0%{?with_doc}
BuildRequires:  python%{pyver}-sphinx
BuildRequires:  python%{pyver}-openstackdocstheme
%endif
BuildRequires:  git
BuildRequires:  openstack-macros

%if 0%{with tests}
# test requirements
BuildRequires:  openstack-dashboard >= 1:14.0.0
BuildRequires:  python%{pyver}-hacking
BuildRequires:  python%{pyver}-manilaclient
BuildRequires:  python%{pyver}-neutronclient
BuildRequires:  python%{pyver}-mock
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

%if 0%{?with_doc}
# generate html docs
%{pyver_bin} setup.py build_sphinx -b html
# remove the sphinx-build-%{pyver} leftovers
rm -fr doc/build/html/.doctrees doc/build/html/.buildinfo
%endif

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
    install -p -D -m 644 ${f} %{buildroot}%{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled/$(f)
done
popd

# NOTE(vkmc) RDO python-django-horizon has a separate folder for local_settings, so we need to create symlinks for the config files
%if 0%{?rhosp} == 0
    for f in %{buildroot}%{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled/_{80,90*}_manila_*.py*; do
        filename=`basename $f`
        ln -s %{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled/${filename} \
            %{buildroot}%{_sysconfdir}/openstack-dashboard/enabled/${filename}
    done
%endif

# local_settings.d allows overriding of settings
pushd .
cd %{buildroot}%{pyver_sitelib}/%{mod_name}/local/local_settings.d
for f in _90_manila_*.py*; do
    install -p -D -m 644 ${f} %{buildroot}%{_datadir}/openstack-dashboard/openstack_dashboard/local/local_settings.d/$(f)
done
popd

%if 0%{?rhosp} == 0
    for f in %{buildroot}%{_datadir}/openstack-dashboard/openstack_dashboard/local/local_settings.d/_90_manila_*.py*; do
        filename=`basename $f`
        ln -s %{_datadir}/openstack-dashboard/openstack_dashboard/local/local_settings.d/${filename} \
            %{buildroot}%{_sysconfdir}/openstack-dashboard/local_settings.d/${filename}
    done
%endif

%check
%if 0%{with tests}
PYTHONPATH=/usr/share/openstack-dashboard/ ./run_tests.sh -N -P
%endif


%files
%if 0%{?with_doc}
%doc doc/build/html
%endif
%doc README.rst
%license LICENSE
%{pyver_sitelib}/%{mod_name}
%{pyver_sitelib}/manila_ui-*-py?.?.egg-info
%{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled/_80_manila_*.py*
%{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled/_90*_manila_*.py*
%{_datadir}/openstack-dashboard/openstack_dashboard/local/local_settings.d/_90_manila_*.py*

%if 0%{?rhosp} == 0
    %{_sysconfdir}/openstack-dashboard/enabled/_80_manila_*.py*
    %{_sysconfdir}/openstack-dashboard/enabled/_90*_manila_*.py*
    %{_sysconfdir}/openstack-dashboard/local_settings.d/_90_manila_*.py*
%endif

%changelog
* Thu Oct 17 2019 RDO <dev@lists.rdoproject.org> 2.19.1-1
- Update to 2.19.1

* Thu Oct 10 2019 RDO <dev@lists.rdoproject.org> 2.19.0-1
- Update to 2.19.0

