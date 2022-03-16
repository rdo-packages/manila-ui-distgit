%{!?sources_gpg: %{!?dlrn:%global sources_gpg 1} }
%global sources_gpg_sign 0x2426b928085a020d8a90d0d879ab7008d0896c8a
%global pypi_name manila-ui
%global mod_name manila_ui

# RDO
%global rhosp 0

%global with_doc 1
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
# Required for tarball sources verification
%if 0%{?sources_gpg} == 1
Source101:        https://tarballs.openstack.org/%{pypi_name}/%{pypi_name}-%{upstream_version}.tar.gz.asc
Source102:        https://releases.openstack.org/_static/%{sources_gpg_sign}.txt
%endif
BuildArch:      noarch

# Required for tarball sources verification
%if 0%{?sources_gpg} == 1
BuildRequires:  /usr/bin/gpgv2
%endif

BuildRequires:  python3-devel
BuildRequires:  python3-pbr
%if 0%{?with_doc}
BuildRequires:  python3-sphinx
BuildRequires:  python3-openstackdocstheme
%endif
BuildRequires:  git-core
BuildRequires:  openstack-macros

%if 0%{with tests}
# test requirements
BuildRequires:  openstack-dashboard >= 1:18.3.1
BuildRequires:  python3-hacking
BuildRequires:  python3-manilaclient
BuildRequires:  python3-neutronclient
BuildRequires:  python3-mock
BuildRequires:  python3-subunit
BuildRequires:  python3-testrepository
BuildRequires:  python3-testscenarios
BuildRequires:  python3-testtools
%endif

Requires: openstack-dashboard >= 1:18.3.1
Requires: python3-django-compressor
Requires: python3-iso8601 >= 0.1.12
Requires: python3-manilaclient >= 2.7.0
Requires: python3-pbr >= 5.5.0
Requires: python3-oslo-utils >= 4.7.0
Requires: python3-keystoneclient >= 1:4.1.1


%description
Manila Management Dashboard


%prep
# Required for tarball sources verification
%if 0%{?sources_gpg} == 1
%{gpgverify}  --keyring=%{SOURCE102} --signature=%{SOURCE101} --data=%{SOURCE0}
%endif
%autosetup -n %{pypi_name}-%{upstream_version} -S git
# Remove bundled egg-info
rm -rf %{pypi_name}.egg-info

%py_req_cleanup

%build
%{py3_build}

%if 0%{?with_doc}
# generate html docs
sphinx-build -W -b html doc/source doc/build/html
# remove the sphinx-build leftovers
rm -fr doc/build/html/.doctrees doc/build/html/.buildinfo
%endif

for lib in %{mod_name}/dashboards/project/*.py; do
  sed '1{\@^#!/usr/bin/env python@d}' $lib > $lib.new &&
  touch -r $lib $lib.new &&
  mv $lib.new $lib
done


%install
%{py3_install}

# Move config to horizon
mkdir -p  %{buildroot}%{_sysconfdir}/openstack-dashboard/enabled
mkdir -p  %{buildroot}%{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled
mkdir -p  %{buildroot}%{_sysconfdir}/openstack-dashboard/local_settings.d
mkdir -p  %{buildroot}%{_datadir}/openstack-dashboard/openstack_dashboard/local/local_settings.d

# enabled allows toggling of panels and plugins
pushd .
cd %{buildroot}%{python3_sitelib}/%{mod_name}/local/enabled
for f in _{80,90*}_manila_*.py*; do
    install -p -D -m 644 ${f} %{buildroot}%{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled/${f}
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
cd %{buildroot}%{python3_sitelib}/%{mod_name}/local/local_settings.d
for f in _90_manila_*.py*; do
    install -p -D -m 644 ${f} %{buildroot}%{_datadir}/openstack-dashboard/openstack_dashboard/local/local_settings.d/${f}
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
%{python3_sitelib}/%{mod_name}
%{python3_sitelib}/manila_ui-*-py%{python3_version}.egg-info
%{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled/_80_manila_*.py*
%{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled/_90*_manila_*.py*
%{_datadir}/openstack-dashboard/openstack_dashboard/local/local_settings.d/_90_manila_*.py*

%if 0%{?rhosp} == 0
    %{_sysconfdir}/openstack-dashboard/enabled/_80_manila_*.py*
    %{_sysconfdir}/openstack-dashboard/enabled/_90*_manila_*.py*
    %{_sysconfdir}/openstack-dashboard/local_settings.d/_90_manila_*.py*
%endif

%changelog
