# vim: expandtab
Name:           miredo
Version:        1.1.6
Release:        2%{?dist}
Summary:        Tunneling of IPv6 over UDP through NATs

Group:          Applications/Internet
License:        GPLv2+
URL:            http://www.simphalempin.com/dev/miredo/
Source0:        http://www.remlab.net/files/miredo/miredo-%{version}.tar.bz2
Source1:        miredo-client.init
Source2:        miredo-server.init
%if 0%{?rhel}
Source3:        isatapd.init
%endif
Patch0:         miredo-config-not-exec
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:    libcap-devel Judy-devel
Requires(pre):    shadow-utils
Requires(post):   chkconfig, /sbin/ldconfig
# This is for /sbin/service
Requires(preun):  chkconfig, initscripts
Requires(postun): initscripts, /sbin/ldconfig


%description
Miredo is an implementation of the "Teredo: Tunneling IPv6 over UDP
through NATs" proposed Internet standard (RFC4380). It can serve
either as a Teredo client, a stand-alone Teredo relay, or a Teredo
server. It is meant to provide IPv6 connectivity to hosts behind NAT
devices, most of which do not support IPv6, and not even
IPv6-over-IPv4 (including 6to4).


%package devel
Summary:        Header files, libraries and development documentation for %{name}
Group:          Development/Libraries
Requires:       %{name} = %{version}-%{release}

%description devel
This package contains the header files, development libraries and development
documentation for %{name}. If you would like to develop programs using %{name},
you will need to install %{name}-devel.


%prep
%setup -q
%patch0 -p1 

%build
%configure \
               --disable-static \
               --disable-rpath \
               --with-Judy \
               --enable-miredo-user
# rpath does not really work
sed -i 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g' libtool
sed -i 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' libtool
make %{?_smp_mflags}


%install
rm -rf %{buildroot}
make install DESTDIR=%{buildroot} INSTALL='install -p'
%find_lang %{name}
mkdir rpmdocs
mv %{buildroot}%{_docdir}/miredo/examples rpmdocs/
mkdir -p %{buildroot}%{_initrddir}
install -p -m 755 %{SOURCE1} %{buildroot}%{_initrddir}/miredo-client
install -p -m 755 %{SOURCE2} %{buildroot}%{_initrddir}/miredo-server
%if 0%{?rhel}
install -p -m 755 %{SOURCE3} %{buildroot}%{_initrddir}/isatapd
%endif
rm -f %{buildroot}%{_libdir}/lib*.la
touch %{buildroot}%{_sysconfdir}/miredo/miredo-server.conf


%pre
getent group miredo >/dev/null || groupadd -r miredo
getent passwd miredo >/dev/null || useradd -r -g miredo -d /etc/miredo -s /sbin/nologin \
     -c "Miredo Daemon" miredo
exit 0


%post
/sbin/ldconfig
/sbin/chkconfig --add miredo-client
/sbin/chkconfig --add miredo-server
%if 0%{?rhel}
/sbin/chkconfig --add isatapd
%endif


%preun
if [ $1 = 0 ] ; then
    %if 0%{?rhel}
    /sbin/service isatapd stop >/dev/null 2>&1
    %endif
    /sbin/service miredo-server stop >/dev/null 2>&1
    /sbin/service miredo-client stop >/dev/null 2>&1
    /sbin/chkconfig --del miredo-client
    /sbin/chkconfig --del miredo-server
    %if 0%{?rhel}
    /sbin/chkconfig --del isatapd
    %endif
fi


%postun
/sbin/ldconfig
if [ "$1" -ge "1" ] ; then
    %if 0%{?rhel}
    /sbin/service isatapd condrestart >/dev/null 2>&1 || :
    %endif
    /sbin/service miredo-server condrestart >/dev/null 2>&1 || :
    /sbin/service miredo-client condrestart >/dev/null 2>&1 || :
fi


%clean
rm -rf %{buildroot}


%files -f %{name}.lang
%defattr(-,root,root,-)
%doc AUTHORS ChangeLog COPYING NEWS README THANKS TODO rpmdocs/*
%doc %{_mandir}/man?/miredo*
%doc %{_mandir}/man1/teredo-mire*
%dir %{_sysconfdir}/miredo
%config(noreplace) %{_sysconfdir}/miredo/miredo.conf
%config(noreplace) %{_sysconfdir}/miredo/client-hook
%ghost %config(noreplace,missingok) %{_sysconfdir}/miredo/miredo-server.conf
%{_sbindir}/miredo
%{_sbindir}/miredo-checkconf
%{_sbindir}/miredo-server
%{_bindir}/teredo-mire
%{_libdir}/libteredo.so.*
%{_libdir}/libtun6.so.*
%{_initrddir}/miredo-client
%{_initrddir}/miredo-server

%if 0%{?rhel}
%{_sbindir}/isatapd
%doc %{_mandir}/man5/isatapd.conf*
%doc %{_mandir}/man8/isatapd*
%{_initrddir}/isatapd
%endif


%files devel
%defattr(-,root,root,-)
%{_includedir}/libteredo/
%{_includedir}/libtun6/
%{_libdir}/libteredo.so
%{_libdir}/libtun6.so


%changelog
* Sat Jun 28 2009 Jens Kuehnel <fedora-package@jens.kuehnel.org> 1.1.6-2
- renamed miredo startscript to miredo-client
- preliminary preperation for EL
- miredo-server.conf ghosted
- removed .la files instead excluding of them
- fixed ldconfig requires

* Sat Jun 27 2009 Jens Kuehnel <fedora-package@jens.kuehnel.org> 1.1.6-1
- ReInitiate Fedora package review
- update to 1.1.6
- removed isatap stuff
- don't start it by default

* Sun Oct 05 2008 Charles R. Anderson <cra@wpi.edu> 1.1.5-1
- Initial Fedora package based on Dries miredo.spec 5059
- Updated to 1.1.5
- disable-static libs
- remove hardcoded rpaths
- create initscripts for client, server, and isatap daemon
- create system user miredo for daemon to setid to
