%define product ERP5SyncML
%define version 0.9.20060116
# If we get the code from the CVS, the release will be always the first
%define release 1

%define zope_home %{_prefix}/lib/zope
%define software_home %{zope_home}/lib/python

Summary:   SyncML for ERP5
Name:      zope-%{product}
Version:   %{version}
Release:   %mkrel %{release}
License:   GPL
Group:     System/Servers
URL:       http://www.erp5.org
Source0:   %{product}-%{version}.tar.bz2
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-rootdir
BuildArch: noarch
Requires:  zope-erp5 zope-ERP5Type erp5diff

#----------------------------------------------------------------------
%description
ERP5Type contains most importants objects for ERP5. ERP5Type defines
most of methods that will be used by every object. It also implements
the Rapid Application Developpement feature used in ERP5.

#----------------------------------------------------------------------
%prep
%setup -c

%build


%install
%{__rm} -rf %{buildroot}
%{__mkdir_p} %{buildroot}/%{software_home}/Products
%{__cp} -a * %{buildroot}%{software_home}/Products/


%clean
%{__rm} -rf %{buildroot}

%post
if [ "`%{_prefix}/bin/zopectl status`" != "daemon manager not running" ] ; then
  service zope restart
fi

%postun
if [ -f "%{_prefix}/bin/zopectl" ] && [ "`%{_prefix}/bin/zopectl status`" != "daemon manager not running" ] ; then
  service zope restart
fi

%files
%defattr(0644, root, root, 0755)
%doc VERSION.txt
%{software_home}/Products/*

#----------------------------------------------------------------------
%changelog
* Mon Jan 16 2006 Kevin Deldycke <kevin@nexedi.com> 0.9.20060116-1mdk
- New build from the CVS

* Tue Jan 10 2006 Kevin Deldycke <kevin@nexedi.com> 0.9.20060110-1mdk
- New release for Mandriva 2006
- Spec file updated

* Tue Sep 01 2004 Sebastien Robin <seb@nexedi.com> 0.8-1mdk
- Final relase for Mandrake 10.1

* Thu Jun 10 2004 Sebastien Robin <seb@nexedi.com> 0.1-5mdk
- New Release For Mandkrake 10.1

* Mon Sep 08 2003 Sebastien Robin <seb@nexedi.com> 0.1-3mdk
- Changed permissions on files

* Wed Sep 05 2003 Sebastien Robin <seb@nexedi.com> 0.1-2mdk
- Update spec in order to follows Mandrake Rules

* Mon May 12 2003 Sebastien Robin <seb@nexedi.com> 0.1-1nxd
- Create the spec file
