Summary: Gnome user file sharing
Name: gnome-user-share
Version: 2.28.2
Release: 3%{?dist}
License: GPLv2+
Group: System Environment/Libraries
URL: http://www.gnome.org
Source0: http://download.gnome.org/sources/gnome-user-share/2.28/%{name}-%{version}.tar.bz2
# http://bugzilla.gnome.org/show_bug.cgi?id=578090
Patch0: menu-path.patch
# http://bugzilla.gnome.org/show_bug.cgi?id=558244
# https://bugzilla.gnome.org/show_bug.cgi?id=600499
Patch1: 0001-Bug-558244-Enabling-gnome-user-share-requires-cha.patch
%define		_default_patch_fuzz 2
Patch2: 0001-Use-same-directories-in-nautilus-bar-and-app.patch

# updated translations
# https://bugzilla.redhat.com/show_bug.cgi?id=589208
Patch3: gnome-user-share-translations.patch

BuildRequires: intltool automake autoconf libtool


BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
ExcludeArch: s390 s390x
Requires: httpd >= 2.2.0
Requires: obex-data-server >= 0.3
Requires: mod_dnssd
BuildRequires: GConf2-devel pkgconfig
BuildRequires: gtk2-devel >= 2.4.0
BuildRequires: httpd >= 2.2.0 mod_dnssd >= 0.6
BuildRequires: gnome-bluetooth-libs-devel
BuildRequires: libcanberra-devel
BuildRequires: desktop-file-utils
BuildRequires: gnome-doc-utils
BuildRequires: libselinux-devel
BuildRequires: dbus-glib-devel
BuildRequires: libnotify-devel
BuildRequires: nautilus-devel
BuildRequires: unique-devel
BuildRequires: gettext
BuildRequires: perl(XML::Parser) intltool
Requires(post): GConf2
Requires(post): scrollkeeper
Requires(postun): scrollkeeper
Requires(pre): GConf2
Requires(preun): GConf2

%description

gnome-user-share is a small package that binds together various free
software projects to bring easy to use user-level file sharing to the
masses.

The program is meant to run in the background when the user is logged
in, and when file sharing is enabled a webdav server is started that
shares the $HOME/Public folder. The share is then published to all
computers on the local network using mDNS/rendezvous, so that it shows
up in the Network location in GNOME.

The program also allows to share files using ObexFTP over Bluetooth.

%prep
%setup -q
%patch0 -p1 -b .menu-path
%patch1 -p1 -b .cluebar
%patch2 -p1 -b .dirs
%patch3 -p1 -b .translations

autoreconf -f -i

%build
%configure
make %{?_smp_mflags}

%install
rm -rf $RPM_BUILD_ROOT

export GCONF_DISABLE_MAKEFILE_SCHEMA_INSTALL=1
make install DESTDIR=$RPM_BUILD_ROOT
unset GCONF_DISABLE_MAKEFILE_SCHEMA_INSTALL

rm -f $RPM_BUILD_ROOT%{_libdir}/nautilus/extensions-2.0/*.la

desktop-file-install --vendor gnome --delete-original                   \
  --dir $RPM_BUILD_ROOT%{_datadir}/applications			        \
  --add-only-show-in GNOME                                              \
  --add-category X-Red-Hat-Base                                         \
  $RPM_BUILD_ROOT%{_datadir}/applications/*.desktop

%find_lang gnome-user-share --with-gnome

# save space by linking identical images in translated docs
helpdir=$RPM_BUILD_ROOT%{_datadir}/gnome/help/%{name}
for f in $helpdir/C/figures/*.png; do
  b="$(basename $f)"
  for d in $helpdir/*; do
    if [ -d "$d" -a "$d" != "$helpdir/C" ]; then
      g="$d/figures/$b"
      if [ -f "$g" ]; then
        if cmp -s $f $g; then
          rm "$g"; ln -s "../../C/figures/$b" "$g"
        fi
      fi
    fi
  done
done

%clean
rm -rf $RPM_BUILD_ROOT

%post
scrollkeeper-update -q
export GCONF_CONFIG_SOURCE=`gconftool-2 --get-default-source`
gconftool-2 --makefile-install-rule %{_sysconfdir}/gconf/schemas/desktop_gnome_file_sharing.schemas > /dev/null || :
if [ -x /usr/bin/gtk-update-icon-cache ]; then
  /usr/bin/gtk-update-icon-cache --quiet %{_datadir}/icons/hicolor
fi

%pre
if [ "$1" -gt 1 ]; then
  export GCONF_CONFIG_SOURCE=`gconftool-2 --get-default-source`
  gconftool-2 --makefile-uninstall-rule %{_sysconfdir}/gconf/schemas/desktop_gnome_file_sharing.schemas > /dev/null || :
fi

%preun
if [ "$1" -eq 0 ]; then
  export GCONF_CONFIG_SOURCE=`gconftool-2 --get-default-source`
  gconftool-2 --makefile-uninstall-rule %{_sysconfdir}/gconf/schemas/desktop_gnome_file_sharing.schemas > /dev/null || :
fi

%postun
scrollkeeper-update -q
if [ -x /usr/bin/gtk-update-icon-cache ]; then
  /usr/bin/gtk-update-icon-cache --quiet %{_datadir}/icons/hicolor
fi

%files -f gnome-user-share.lang
%defattr(-,root,root,-)
%doc README COPYING NEWS AUTHORS
%{_bindir}/*
%{_libexecdir}/*
%{_datadir}/gnome-user-share
%{_datadir}/applications/*
%{_sysconfdir}/xdg/autostart/gnome-user-share.desktop
%{_sysconfdir}/gconf/schemas/*
%{_datadir}/icons/hicolor/*/apps/gnome-obex-server.png
%{_libdir}/nautilus/extensions-2.0/*.so

%changelog
* Mon May 17 2010 Matthias Clasen <mclasen@redhat.com> 2.28.2-3
- Updated translations
Resolves: #589208

* Thu Jan 21 2010 Bastien Nocera <bnocera@redhat.com> 2.28.2-2
- Don't build on s390(x), no Obex there (#557208)
Related: rhbz#543948

* Fri Dec 11 2009 Bastien Nocera <bnocera@redhat.com> 2.28.2-1
- Update to 2.28.2

* Tue Nov 10 2009 Bastien Nocera <bnocera@redhat.com> 2.28.1-3
- Fix crasher on exit when ObexFTP isn't started (#533977)

* Tue Nov 03 2009 Bastien Nocera <bnocera@redhat.com> 2.28.1-2
- Update share bar code to use the same directories as
  the sharing code itself

* Mon Oct 26 2009 Bastien Nocera <bnocera@redhat.com> 2.28.1-1
- Update to 2.28.1

* Mon Sep 21 2009 Bastien Nocera <bnocera@redhat.com> 2.28.0-1
- Update to 2.28.0

* Tue Sep 08 2009 Bastien Nocera <bnocera@redhat.com> 2.27.0-3
- Add a cluebar to have easy access to the file sharing preferences

* Mon Sep 07 2009 Bastien Nocera <bnocera@redhat.com> 2.27.0-2
- Init i18n system for gnome-user-share

* Wed Sep 02 2009 Bastien Nocera <bnocera@redhat.com> 2.27.0-1
- Update to 2.27.0

* Thu Aug 20 2009 Tomas Bzatek <tbzatek@redhat.com> - 2.26.0-6
- Do not localize realm in passwd files (#500123)

* Tue Aug 11 2009 Bastien Nocera <bnocera@redhat.com> 2.26.0-5
- Fix source URL

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.26.0-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Thu Jul  2 2009 Matthias Clasen <mclasen@redhat.com> - 2.26.0-3
- Rebuild to shrink GConf schemas

* Sun Apr  5 2009 Matthias Clasen <mclasen@redhat.com> - 2.26.0-2
- Fix a menu reference in the docs (#494253)

* Mon Mar 16 2009 - Bastien Nocera <bnocera@redhat.com> - 2.26.0-1
- Update to 2.26.0

* Tue Mar 03 2009 - Bastien Nocera <bnocera@redhat.com> - 2.25.92-1
- Update to 2.25.92

* Tue Feb 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.25.91-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Tue Feb 03 2009 - Bastien Nocera <bnocera@redhat.com> - 2.25.91-1
- Update to 2.25.91

* Tue Feb 03 2009 - Bastien Nocera <bnocera@redhat.com> - 2.25.90-1
- Update to 2.25.90

* Thu Jan 29 2009 - Bastien Nocera <bnocera@redhat.com> - 2.25.5-2
- Export the user through the TXT record with the new mod_dnssd

* Tue Jan 27 2009 - Bastien Nocera <bnocera@redhat.com> - 2.25.5-1
- Update to 2.25.5

* Wed Dec 17 2008 - Bastien Nocera <bnocera@redhat.com> - 0.41-1
- Update to 0.41

* Mon Sep 22 2008 - Bastien Nocera <bnocera@redhat.com> - 0.40-3
- Add missing libnotify BR

* Mon Sep 22 2008 - Bastien Nocera <bnocera@redhat.com> - 0.40-2
- Add missing intltool BR

* Mon Sep 22 2008 - Bastien Nocera <bnocera@redhat.com> - 0.40-1
- Update to 0.40

* Mon Sep 22 2008 - Bastien Nocera <bnocera@redhat.com> - 0.31-3
- Add patch to port to BlueZ 4.x API

* Sun May  4 2008 Matthias Clasen <mclasen@redhat.com> - 0.31-2
- Fix source url

* Thu Apr 03 2008 - Bastien Nocera <bnocera@redhat.com> - 0.31-1
- Update to 0.31

* Mon Mar 31 2008 - Bastien Nocera <bnocera@redhat.com> - 0.30-1
- Update to 0.30
- Fixes left-over httpd processes after logout

* Sun Feb 24 2008 - Bastien Nocera <bnocera@redhat.com> - 0.22-1
- Update to 0.22

* Mon Feb 18 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 0.21-2
- Autorebuild for GCC 4.3

* Fri Jan 25 2008 - Bastien Nocera <bnocera@redhat.com> - 0.21-1
- Update to 0.21

* Tue Jan 22 2008 - Bastien Nocera <bnocera@redhat.com> - 0.20-1
- Update to 0.20
- Remove obsolete patches

* Tue Sep 11 2007 Matthias Clasen <mclasen@redhat.com> - 0.11-9
- Fix a memory leak

* Tue Aug 28 2007 Fedora Release Engineering <rel-eng at fedoraproject dot org> - 0.11-8
- Rebuild for selinux ppc32 issue.

* Tue Aug  7 2007 Matthias Clasen <mclasen@redhat.com> - 0.11-7
- Update license field

* Thu Jul 12 2007 Matthias Clasen <mclasen@redhat.com> - 0.11-6
- Disable the password entry for "never"

* Thu Jul 12 2007 Owen Taylor <otaylor@redhat.com> - 0.11-5
- Regenerate configure since patch1 changes configure.in

* Thu Jul 12 2007 Owen Taylor <otaylor@redhat.com> - 0.11-4
- Add a patch from SVN to export DBUS session ID via Avahi (b.g.o #455307)

* Mon Apr 23 2007 Matthias Clasen  <mclasen@redhat.com> - 0.11-3
- Improve %%description (#235677)

* Fri Mar 23 2007 Matthias Clasen  <mclasen@redhat.com> - 0.11-2
- Don't hardwire invisible char (#233676)

* Tue Mar  6 2007 Alexander Larsson <alexl@redhat.com> - 0.11-1
- Update to 0.11 with xdg-user-dirs support

* Wed Jan 24 2007 Matthias Clasen <mclasen@redhat.com> 0.10-6
- Add better categories to the desktop file

* Sun Oct 01 2006 Jesse Keating <jkeating@redhat.com> - 0.10-5
- rebuilt for unwind info generation, broken in gcc-4.1.1-21

* Thu Sep 21 2006 Nalin Dahyabhai <nalin@redhat.com> - 0.10-4
- add missing BuildRequires: on httpd, so that the configure script can find
  the binary

* Wed Jul 12 2006 Jesse Keating <jkeating@redhat.com> - 0.10-3.1
- rebuild

* Mon May 29 2006 Alexander Larsson <alexl@redhat.com> - 0.10-3
- buildrequire gettext and perl-XML-Parser (#193391)

* Thu Apr 20 2006 Matthias Clasen <mclasen@redhat.com> 0.10-2
- Update to 0.10

* Wed Mar 01 2006 Karsten Hopp <karsten@redhat.de> 0.9-3
- BuildRequires: gtk2-devel, libglade2-devel, libselinux-devel

* Fri Feb 10 2006 Jesse Keating <jkeating@redhat.com> - 0.9-2.2
- bump again for double-long bug on ppc(64)

* Tue Feb 07 2006 Jesse Keating <jkeating@redhat.com> - 0.9-2.1
- rebuilt for new gcc4.1 snapshot and glibc changes

* Fri Feb  3 2006 Alexander Larsson <alexl@redhat.com> 0.9-2
- Patch config for apache 2.2

* Fri Dec 09 2005 Jesse Keating <jkeating@redhat.com>
- rebuilt

* Tue Nov 22 2005 Alexander Larsson <alexl@redhat.com> - 0.9-1
- New release with avahi 0.6 support

* Mon Nov 14 2005 Alexander Larsson <alexl@redhat.com> - 0.8-1
- update to 0.8

* Wed Nov  9 2005 Alexander Larsson <alexl@redhat.com> - 0.7-1
- New version, with desktop file

* Wed Nov  9 2005 Alexander Larsson <alexl@redhat.com> - 0.6-1
- New version, switch to avahi
- Handle translations

* Fri Dec  3 2004 Alexander Larsson <alexl@redhat.com> - 0.4-1
- New version

* Fri Nov 26 2004 Alexander Larsson <alexl@redhat.com> - 0.3-1
- New version

* Thu Sep  9 2004 Alexander Larsson <alexl@redhat.com> - 0.2-1
- New version

* Wed Sep  8 2004 Alexander Larsson <alexl@redhat.com> - 0.1-1
- Initial Build

