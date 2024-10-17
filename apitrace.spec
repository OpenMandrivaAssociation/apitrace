#global commit c54d99563414cd178abec7cf7d9663eb949a0f51
#global shortcommit %(c=%{commit}; echo ${c:0:7})

# Update to submodule revision as in https://github.com/apitrace/apitrace/tree/master/thirdparty when updating
%global libbacktrace_commit dedbe13fda00253fe5d4f2fb812c909729ed5937
%global libbacktrace_shortcommit %(c=%{libbacktrace_commit}; echo ${c:0:7})

Name:           apitrace
Version:        11.1
Release:        3%{?commit:.git%{shortcommit}}%{?dist}
Summary:        Tools for tracing OpenGL

License:        MIT
URL:            https://apitrace.github.io/
%if 0%{?commit:1}
# git clone --recursive https://github.com/apitrace/apitrace.git
# cd apitrace
# git archive --prefix=apitrace-$commit/ -o ../apitrace-${commit:0:7}.tar $commit
# git submodule foreach --recursive "git archive --prefix=apitrace-$commit/\$path/ --output=\$sha1.tar HEAD && tar --concatenate --file=$(pwd)/../apitrace-${commit:0:7}.tar \$sha1.tar && rm \$sha1.tar"
# cd ..
# gzip apitrace-${commit:0:7}.tar
Source0:        apitrace-%{shortcommit}.tar.gz
%else
Source0:        https://github.com/apitrace/apitrace/archive/%{version}/apitrace-%{version}.tar.gz
%endif
Source1:        https://github.com/ianlancetaylor/libbacktrace/archive/%{libbacktrace_commit}/libbacktrace-%{libbacktrace_shortcommit}.tar.gz
Source2:        qapitrace.desktop
Source3:        qapitrace.appdata.xml

# Don't require third-party submodules
Patch0:         apitrace_nosubmodules.patch

BuildRequires:  brotli-devel
BuildRequires:  cmake
BuildRequires:  desktop-file-utils
BuildRequires:  gcc-c++
BuildRequires:  gtest-devel
BuildRequires:  libappstream-glib
BuildRequires:  libdwarf-devel
BuildRequires:  libpng-devel
BuildRequires:  make
BuildRequires:  qt5-qtbase-devel
BuildRequires:  qt5-qtwebkit-devel
BuildRequires:  snappy-devel

Requires:       %{name}-libs%{_isa} = %{version}-%{release}
# scripts/snapdiff.py
Requires:       python3-pillow

# See http://fedoraproject.org/wiki/Packaging:No_Bundled_Libraries#Packages_granted_exceptions
Provides:       bundled(md5-plumb)
# See https://fedorahosted.org/fpc/ticket/429
Provides:       bundled(libbacktrace)
# Modofied http://create.stephan-brumme.com/crc32/, see thirdparty/crc32c/README.md
Provides:       bundled(crc32c)


%description
apitrace consists of a set of tools to:
 * trace OpenGL and OpenGL ES  APIs calls to a file;
 * replay OpenGL and OpenGL ES calls from a file
 * inspect OpenGL state at any call while retracing
 * visualize and edit trace files


%package libs
Summary:        Libraries used by apitrace
Requires:       %{name} = %{version}-%{release}

%description libs
Libraries used by apitrace


%package gui
Summary:        Graphical frontend for apitrace
Requires:       %{name}%{_isa} = %{version}-%{release}

%description gui
This package contains qapitrace, the Graphical frontend for apitrace.


%prep
%if 0%{?commit:1}
%autosetup -p1 -n %{name}-%{commit} -a1
%else
%autosetup -p1 -n %{name}-%{version} -a1
%endif

# Remove bundled libraries, except khronos headers
rm -rf `ls -1d thirdparty/* | grep -Ev "(khronos|md5|crc32c|libbacktrace.cmake|support|CMakeLists.txt)"`

# Add bundled libbacktrace
mv libbacktrace-%{libbacktrace_commit} thirdparty/libbacktrace


%build
%cmake -DENABLE_STATIC_SNAPPY=OFF
%cmake_build


%install
%cmake_install

# Install doc through %%doc
rm -rf %{buildroot}%{_docdir}/

# Install desktop file
desktop-file-install --dir=%{buildroot}%{_datadir}/applications/ %{SOURCE2}

# Install appdata file
install -Dpm 0644 %{SOURCE3} %{buildroot}%{_datadir}/appdata/qapitrace.appdata.xml
%{_bindir}/appstream-util validate-relax --nonet %{buildroot}%{_datadir}/appdata/qapitrace.appdata.xml

# highlight.py is not a script
chmod 0644 %{buildroot}%{_libdir}/%{name}/scripts/highlight.py


%check
# If run through ctest, libbacktrace_btest will fail with
#     ERROR: descriptor 3 still open after tests complete
# This is due to https://gitlab.kitware.com/cmake/cmake/-/issues/18863
# So, run the test outside of ctest
pushd %{_vpath_builddir}
ctest --output-on-failure -E libbacktrace_btest
./btest
popd


%files
%license LICENSE
%doc README.markdown docs/*
%{_bindir}/apitrace
%{_bindir}/eglretrace
%{_bindir}/glretrace
%{_bindir}/gltrim

%files libs
%{_libdir}/%{name}/

%files gui
%{_bindir}/qapitrace
%{_datadir}/applications/qapitrace.desktop
%{_datadir}/appdata/qapitrace.appdata.xml
