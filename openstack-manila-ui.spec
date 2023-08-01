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
# we are excluding some BRs from automatic generator
%global excluded_brs doc8 bandit pre-commit hacking flake8-import-order
# Exclude sphinx from BRs if docs are disabled
%if ! 0%{?with_doc}
%global excluded_brs %{excluded_brs} sphinx openstackdocstheme
%endif

Name:           openstack-%{pypi_name}
Version:        XXX
Release:        XXX
Summary:        Manila Management Dashboard

License:        Apache-2.0
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
BuildRequires:  pyproject-rpm-macros
BuildRequires:  git-core
BuildRequires:  openstack-macros
BuildRequires:  openstack-dashboard >= 1:18.3.1

Requires: openstack-dashboard >= 1:18.3.1

%description
Manila Management Dashboard


%prep
# Required for tarball sources verification
%if 0%{?sources_gpg} == 1
%{gpgverify}  --keyring=%{SOURCE102} --signature=%{SOURCE101} --data=%{SOURCE0}
%endif
%autosetup -n %{pypi_name}-%{upstream_version} -S git


sed -i /^[[:space:]]*-c{env:.*_CONSTRAINTS_FILE.*/d tox.ini
sed -i "s/^deps = -c{env:.*_CONSTRAINTS_FILE.*/deps =/" tox.ini
sed -i /^minversion.*/d tox.ini
sed -i /^requires.*virtualenv.*/d tox.ini

# Exclude some bad-known BRs
for pkg in %{excluded_brs}; do
  for reqfile in doc/requirements.txt test-requirements.txt; do
    if [ -f $reqfile ]; then
      sed -i /^${pkg}.*/d $reqfile
    fi
  done
done

# Automatic BR generation
%generate_buildrequires
%if 0%{?with_doc}
  %pyproject_buildrequires -t -e %{default_toxenv},docs
%else
  %pyproject_buildrequires -t -e %{default_toxenv}
%endif

%build
%pyproject_wheel

%if 0%{?with_doc}
# generate html docs
%tox -e docs
# remove the sphinx-build leftovers
rm -fr doc/build/html/.doctrees doc/build/html/.buildinfo
%endif

for lib in %{mod_name}/dashboards/project/*.py; do
  sed '1{\@^#!/usr/bin/env python@d}' $lib > $lib.new &&
  touch -r $lib $lib.new &&
  mv $lib.new $lib
done


%install
%pyproject_install

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
%{python3_sitelib}/manila_ui-*.dist-info
%{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled/_80_manila_*.py*
%{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled/_90*_manila_*.py*
%{_datadir}/openstack-dashboard/openstack_dashboard/local/local_settings.d/_90_manila_*.py*

%if 0%{?rhosp} == 0
    %{_sysconfdir}/openstack-dashboard/enabled/_80_manila_*.py*
    %{_sysconfdir}/openstack-dashboard/enabled/_90*_manila_*.py*
    %{_sysconfdir}/openstack-dashboard/local_settings.d/_90_manila_*.py*
%endif

%changelog
