%global _hardened_build 1

Name:               pmacct
Version:            1.6.2
Release:            1
Summary:            Accounting and aggregation toolsuite for IPv4 and IPv6
License:            GPLv2+
Group:              Applications/Engineering
URL:                http://www.pmacct.net/
Source0:            pmacct-%{version}.tar.gz
Source1:            nfacctd.sysvinit
Source2:            nfacctd.sysconfig
Source3:            pmacctd.sysvinit
Source4:            pmacctd.sysconfig
Source5:            sfacctd.sysvinit
Source6:            sfacctd.sysconfig

Patch1:             pmacct-fix-implicit-pointer-decl.diff

BuildRequires:      gcc
BuildRequires:      make
BuildRequires:      libpcap-devel
BuildRequires:      pkgconfig
BuildRequires:      sqlite-devel >= 3.0.0
BuildRequires:      pkgconfig(geoip)
BuildRequires:      pkgconfig(jansson)

%description
pmacct is a small set of passive network monitoring tools to measure, account,
classify and aggregate IPv4 and IPv6 traffic; a pluggable and flexible
architecture allows to store the collected traffic data into memory tables or
SQL (MySQL, SQLite, PostgreSQL) databases. pmacct supports fully customizable
historical data breakdown, flow sampling, filtering and tagging, recovery
actions, and triggers. Libpcap, sFlow v2/v4/v5 and NetFlow v1/v5/v7/v8/v9 are
supported, both unicast and multicast. Also, a client program makes it easy to
export data to tools like RRDtool, GNUPlot, Net-SNMP, MRTG, and Cacti.

%prep
%autosetup -p1

# fix permissions
chmod -x sql/pmacct-*

%build
export CFLAGS="%{optflags} -Wno-return-type"
%configure \
    --sysconfdir=%{_sysconfdir}/%{name} \
    --prefix=%{_prefix} \
    --exec-prefix=%{_exec_prefix} \
    --sbindir=%{_sbindir} \
    --enable-l2 \
    --enable-ipv6 \
    --enable-sqlite3 \
    --enable-geoip \
    --enable-jansson \
    --enable-64bit \
    --enable-threads

make %{?_smp_mflags}

%install
make DESTDIR=%{buildroot} install %{?_smp_mflags}

# install sample configuration files
install -Dp examples/nfacctd-sql_v2.conf.example %{buildroot}/%{_sysconfdir}/%{name}/nfacctd.conf
install -Dp examples/pmacctd-sql_v2.conf.example %{buildroot}/%{_sysconfdir}/%{name}/pmacctd.conf

# install systemd units
install -d %{buildroot}/%{_initddir}
install %{SOURCE1} %{buildroot}/%{_initddir}/nfacctd
install %{SOURCE3} %{buildroot}/%{_initddir}/pmacctd
install %{SOURCE5} %{buildroot}/%{_initddir}/sfacctd
#
install -d %{buildroot}/%{_sysconfdir}/sysconfig/%{name}
install %{SOURCE2} %{buildroot}/%{_sysconfdir}/sysconfig/%{name}/nfacctd
install %{SOURCE4} %{buildroot}/%{_sysconfdir}/sysconfig/%{name}/pmacctd
install %{SOURCE6} %{buildroot}/%{_sysconfdir}/sysconfig/%{name}/sfacctd

%post
chkconfig --add pmacctd
chkconfig --add nfacctd
chkconfig --add sfacctd

%preun
if [ $1 -eq 0 ] ; then
    /sbin/service pmacctd stop >/dev/null 2>&1
    /sbin/service nfacctd stop >/dev/null 2>&1
    /sbin/service sfacctd stop >/dev/null 2>&1
    /sbin/chkconfig --del pmacctd
    /sbin/chkconfig --del nfacctd
    /sbin/chkconfig --del sfacctd
fi

%files
%defattr(-,root,root)
%doc AUTHORS ChangeLog CONFIG-KEYS COPYING FAQS TOOLS UPGRADE
%doc docs examples sql
%{_bindir}/pmacct
#
%{_sbindir}/nfacctd
%{_sbindir}/pmacctd
%{_sbindir}/sfacctd
%{_sbindir}/pmbgpd
%{_sbindir}/pmbmpd
%{_sbindir}/pmtelemetryd
#
%attr(755,root,root) %{_initddir}/pmacctd
%attr(755,root,root) %{_initddir}/nfacctd
%attr(755,root,root) %{_initddir}/sfacctd
#
%attr(755,root,root) %{_sysconfdir}/sysconfig/%{name}/nfacctd
%attr(755,root,root) %{_sysconfdir}/sysconfig/%{name}/pmacctd
%attr(755,root,root) %{_sysconfdir}/sysconfig/%{name}/sfacctd
#
%dir %{_sysconfdir}/pmacct
%attr(600,root,root) %config(noreplace) %{_sysconfdir}/pmacct/nfacctd.conf
%attr(600,root,root) %config(noreplace) %{_sysconfdir}/pmacct/pmacctd.conf

%changelog
* Fri May 05 2017 Quest <quest@lysator.liu.se> - 1.6.2-1
- EPEL 6 version

* Wed Jan 13 2016 Betsy Alpert <ealpert@iix.net> - 1.5.2-3
- Added build support for AMQP/RabbitMQ

* Mon Dec 21 2015 Arun Babu Neelicattu <arun.neelicattu@gmail.com> - 1.5.2-2
- Enable ULOG

* Sun Dec 13 2015 Arun Babu Neelicattu <arun.neelicattu@gmail.com> - 1.5.2-1
- Initial packaging based on OpenSUSE rpms packaged by Peter Nixon and available
  at http://download.opensuse.org/repositories/server:/monitoring/
