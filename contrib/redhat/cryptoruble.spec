Name:           cryptoruble
Version:        0.6.3
Release:        1%{?dist}
Summary:        Cryptoruble Wallet
Group:          Applications/Internet
Vendor:         Cryptoruble
License:        GPLv3
URL:            https://www.cryptoruble.com
Source0:        %{name}-%{version}.tar.gz
BuildRoot:      %(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)
BuildRequires:  autoconf automake libtool gcc-c++ openssl-devel >= 1:1.0.2d libdb4-devel libdb4-cxx-devel miniupnpc-devel boost-devel boost-static
Requires:       openssl >= 1:1.0.2d libdb4 libdb4-cxx miniupnpc logrotate

%description
Cryptoruble Wallet

%prep
%setup -q

%build
./autogen.sh
./configure
make

%install
%{__rm} -rf $RPM_BUILD_ROOT
%{__mkdir} -p $RPM_BUILD_ROOT%{_bindir} $RPM_BUILD_ROOT/etc/cryptoruble $RPM_BUILD_ROOT/etc/ssl/cru $RPM_BUILD_ROOT/var/lib/cru/.cryptoruble $RPM_BUILD_ROOT/usr/lib/systemd/system $RPM_BUILD_ROOT/etc/logrotate.d
%{__install} -m 755 src/cryptorubled $RPM_BUILD_ROOT%{_bindir}
%{__install} -m 755 src/cryptoruble-cli $RPM_BUILD_ROOT%{_bindir}
%{__install} -m 600 contrib/redhat/cryptoruble.conf $RPM_BUILD_ROOT/var/lib/cru/.cryptoruble
%{__install} -m 644 contrib/redhat/cryptorubled.service $RPM_BUILD_ROOT/usr/lib/systemd/system
%{__install} -m 644 contrib/redhat/cryptorubled.logrotate $RPM_BUILD_ROOT/etc/logrotate.d/cryptorubled
%{__mv} -f contrib/redhat/cru $RPM_BUILD_ROOT%{_bindir}

%clean
%{__rm} -rf $RPM_BUILD_ROOT

%pretrans
getent passwd cru >/dev/null && { [ -f /usr/bin/cryptorubled ] || { echo "Looks like user 'cru' already exists and have to be deleted before continue."; exit 1; }; } || useradd -r -M -d /var/lib/cru -s /bin/false cru

%post
[ $1 == 1 ] && {
  sed -i -e "s/\(^rpcpassword=MySuperPassword\)\(.*\)/rpcpassword=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1)/" /var/lib/cru/.cryptoruble/cryptoruble.conf
  openssl req -nodes -x509 -newkey rsa:4096 -keyout /etc/ssl/cru/cryptoruble.key -out /etc/ssl/cru/cryptoruble.crt -days 3560 -subj /C=US/ST=Oregon/L=Portland/O=IT/CN=cryptoruble.cru
  ln -sf /var/lib/cru/.cryptoruble/cryptoruble.conf /etc/cryptoruble/cryptoruble.conf
  ln -sf /etc/ssl/cru /etc/cryptoruble/certs
  chown cru.cru /etc/ssl/cru/cryptoruble.key /etc/ssl/cru/cryptoruble.crt
  chmod 600 /etc/ssl/cru/cryptoruble.key
} || exit 0

%posttrans
[ -f /var/lib/cru/.cryptoruble/addr.dat ] && { cd /var/lib/cru/.cryptoruble && rm -rf database addr.dat nameindex* blk* *.log .lock; }
sed -i -e 's|rpcallowip=\*|rpcallowip=0.0.0.0/0|' /var/lib/cru/.cryptoruble/cryptoruble.conf
systcrutl daemon-reload
systcrutl status cryptorubled >/dev/null && systcrutl restart cryptorubled || exit 0

%preun
[ $1 == 0 ] && {
  systcrutl is-enabled cryptorubled >/dev/null && systcrutl disable cryptorubled >/dev/null || true
  systcrutl status cryptorubled >/dev/null && systcrutl stop cryptorubled >/dev/null || true
  pkill -9 -u cru > /dev/null 2>&1
  getent passwd cru >/dev/null && userdel cru >/dev/null 2>&1 || true
  rm -f /etc/ssl/cru/cryptoruble.key /etc/ssl/cru/cryptoruble.crt /etc/cryptoruble/cryptoruble.conf /etc/cryptoruble/certs
} || exit 0

%files
%doc COPYING
%attr(750,cru,cru) %dir /etc/cryptoruble
%attr(750,cru,cru) %dir /etc/ssl/cru
%attr(700,cru,cru) %dir /var/lib/cru
%attr(700,cru,cru) %dir /var/lib/cru/.cryptoruble
%attr(600,cru,cru) %config(noreplace) /var/lib/cru/.cryptoruble/cryptoruble.conf
%attr(4750,cru,cru) %{_bindir}/cryptoruble-cli
%defattr(-,root,root)
%config(noreplace) /etc/logrotate.d/cryptorubled
%{_bindir}/cryptorubled
%{_bindir}/cru
/usr/lib/systemd/system/cryptorubled.service

%changelog
* Thu Aug 31 2017 Aspanta Limited <info@aspanta.com> 0.6.3
- There is no changelog available. Please refer to the CHANGELOG file or visit the website.
