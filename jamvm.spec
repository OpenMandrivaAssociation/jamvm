%define origin          jamvm
%define originver       %{version}

%define _libdir         %{_prefix}/%{_lib}/%{origin}

%define section         free

%define priority        1410
%define javaver         1.5.0
%define buildver        0

%define java_version    %{javaver}.%{buildver}
%define cname           java-%{javaver}-%{origin}

%define sdklnk           java-%{javaver}-%{origin}
%define jrelnk           jre-%{javaver}-%{origin}
%define sdkdir           %{cname}-%{java_version}
%define jredir           %{sdkdir}/jre
%define sdkbindir        %{_jvmdir}/%{sdklnk}/bin
%define jrebindir        %{_jvmdir}/%{jrelnk}/bin
%define jvmjardir        %{_jvmjardir}/%{cname}-%{java_version}

Name:           jamvm
Version:        1.5.3
Release:        %mkrel 3
Epoch:          0
Summary:        Java Virtual Machine which conforms to the JVM specification version 2
Group:          Development/Java
License:        GPL
URL:            http://jamvm.sourceforge.net/
Source0:        http://downloads.sourceforge.net/jamvm/jamvm-%{originver}.tar.gz
BuildRequires:  eclipse-ecj
BuildRequires:  java-1.5.0-gcj-devel
BuildRequires:  java-rpmbuild >= 0:1.5
BuildRequires:  pkgconfig(libffi)
Requires(post): classpath
Requires(postun): classpath
Requires(post): jpackage-utils >= 0:1.6.3
Requires(postun): jpackage-utils >= 0:1.6.3
Provides:       jre-%{javaver}-%{origin} = %{epoch}:%{java_version}-%{release}
Provides:       jre-%{origin} = %{epoch}:%{java_version}-%{release}
Provides:       jre-%{javaver}, java-%{javaver}, jre = %{epoch}:%{javaver}
Provides:       java-%{origin} = %{epoch}:%{java_version}-%{release}
Provides:       java = %{epoch}:%{javaver}
Provides:       jaxp_parser_impl
Provides:       jndi, jndi-ldap, jdbc-stdext, jaas, jta
Provides:       jsse
Provides:       jaxp_transform_impl
Obsoletes:      java-%{javaver}-%{origin}
Provides:       java-%{javaver}-%{origin}
#Provides:      %{origin} = %{epoch}:%{originver}
ExcludeArch:    sparc

%description
JamVM is a new Java Virtual Machine which conforms to the JVM 
specification version 2 (blue book). In comparison to most other VM's 
(free and commercial) it is extremely small, with a stripped 
executable on PowerPC of only ~135K, and Intel 100K. However, unlike 
other small VMs (e.g. KVM) it is designed to support the full 
specification, and includes support for object finalisation, 
Soft/Weak/Phantom References, the Java Native Interface (JNI) and the 
Reflection API.

%prep
%setup -q -n %{origin}-%{originver}
%{__perl} -pi -e 's|lib/classpath|%{_lib}/classpath|' src/dll.c

%build
export CLASSPATH=
export JAVA=%{java}
export JAVAC=%{javac}
export JAR=%{jar}
export JAVADOC=%{javadoc}
%{configure2_5x} \
  --enable-ffi \
  --with-classpath-install-dir=%{_prefix}
%{make}

%install
%{__rm} -rf %{buildroot}
%{makeinstall_std}

%{__mkdir_p} $RPM_BUILD_ROOT%{_jvmdir}/%{jredir}/bin
(cd $RPM_BUILD_ROOT%{_jvmdir}/%{jredir}/bin \
 && %{__ln_s} %{_bindir}/%{origin} java \
 && %{__ln_s} %{_bindir}/grmiregistry rmiregistry)

%{__mkdir_p} $RPM_BUILD_ROOT%{_jvmdir}/%{jredir}/lib

# create extensions symlinks
ln -s %{_datadir}/classpath/glibj.zip $RPM_BUILD_ROOT%{_jvmdir}/%{jredir}/lib/jsse.jar

# extensions handling
install -dm 755 $RPM_BUILD_ROOT%{jvmjardir}
pushd $RPM_BUILD_ROOT%{jvmjardir}
   ln -s %{_jvmdir}/%{jredir}/lib/jaas.jar jaas-%{java_version}.jar
   ln -s %{_jvmdir}/%{jredir}/lib/jdbc-stdext.jar jdbc-stdext-%{java_version}.jar
   ln -s %{_jvmdir}/%{jredir}/lib/jndi.jar jndi-%{java_version}.jar
   ln -s %{_jvmdir}/%{jredir}/lib/jsse.jar jsse-%{java_version}.jar
   for jar in *-%{java_version}.jar ; do
     ln -sf ${jar} $(echo $jar | sed "s|-%{java_version}.jar|-%{javaver}.jar|g")
     ln -sf ${jar} $(echo $jar | sed "s|-%{java_version}.jar|.jar|g")
   done
popd

# versionless symlinks
pushd $RPM_BUILD_ROOT%{_jvmdir}
   ln -s %{jredir} %{jrelnk}
#   ln -s %{sdkdir} %{sdklnk}
popd

pushd $RPM_BUILD_ROOT%{_jvmjardir}
   ln -s %{sdkdir} %{jrelnk}
#   ln -s %{sdkdir} %{sdklnk}
popd

# generate file lists
find $RPM_BUILD_ROOT%{_jvmdir}/%{jredir} -type d \
  | sed 's|'$RPM_BUILD_ROOT'|%dir |' >  %{name}-%{version}-all.files
find $RPM_BUILD_ROOT%{_jvmdir}/%{jredir} -type f -o -type l \
  | sed 's|'$RPM_BUILD_ROOT'||'      >> %{name}-%{version}-all.files

cat %{name}-%{version}-all.files \
  > %{name}-%{version}.files

find $RPM_BUILD_ROOT%{_jvmdir}/%{sdkdir}/bin -type f -o -type l \
  | sed "s|^$RPM_BUILD_ROOT||"      > %{name}-%{version}-sdk-bin.files

%{__rm} -rf %{buildroot}/%{_includedir}

%post
update-alternatives \
  --install %{_bindir}/java java %{_jvmdir}/%{jrelnk}/bin/java %{priority} \
  --slave %{_jvmdir}/jre          jre          %{_jvmdir}/%{jrelnk} \
  --slave %{_jvmjardir}/jre       jre_exports  %{_jvmjardir}/%{jrelnk} \
  --slave %{_bindir}/rmiregistry  rmiregistry  %{_jvmdir}/%{jrelnk}/bin/rmiregistry

update-alternatives \
  --install %{_jvmdir}/jre-%{origin} \
      jre_%{origin} %{_jvmdir}/%{jrelnk} %{priority} \
  --slave %{_jvmjardir}/jre-%{origin} \
      jre_%{origin}_exports %{_jvmjardir}/%{jrelnk}

update-alternatives \
  --install %{_jvmdir}/jre-%{javaver} \
      jre_%{javaver} %{_jvmdir}/%{jrelnk} %{priority} \
  --slave %{_jvmjardir}/jre-%{javaver} \
      jre_%{javaver}_exports %{_jvmjardir}/%{jrelnk}

# rt.jar
ln -sf \
  %{_datadir}/classpath/glibj.zip \
  %{_jvmdir}/%{cname}-%{java_version}/jre/lib/rt.jar

# jaas.jar
ln -sf \
  %{_datadir}/classpath/glibj.zip \
  %{_jvmdir}/%{cname}-%{java_version}/jre/lib/jaas.jar

# jdbc-stdext.jar
ln -sf \
  %{_datadir}/classpath/glibj.zip \
  %{_jvmdir}/%{cname}-%{java_version}/jre/lib/jdbc-stdext.jar

# jndi.jar
ln -sf \
  %{_datadir}/classpath/glibj.zip \
  %{_jvmdir}/%{cname}-%{java_version}/jre/lib/jndi.jar

# jaxp_parser_impl
update-alternatives --install %{_javadir}/jaxp_parser_impl.jar \
  jaxp_parser_impl \
  %{_datadir}/classpath/glibj.zip 20

# jaxp_transform_impl
update-alternatives --install %{_javadir}/jaxp_transform_impl.jar \
  jaxp_transform_impl \
  %{_datadir}/classpath/glibj.zip 20

%postun
if [ $1 -eq 0 ] ; then
   update-alternatives --remove java %{_jvmdir}/%{jrelnk}/bin/java 
   update-alternatives --remove jre_%{origin}  %{_jvmdir}/%{jrelnk}
   update-alternatives --remove jre_%{javaver} %{_jvmdir}/%{jrelnk}
   update-alternatives --remove jaxp_parser_impl \
     %{_datadir}/classpath/glibj.zip
   update-alternatives --remove jaxp_transform_impl \
     %{_datadir}/classpath/glibj.zip
fi

%files -f %{name}-%{version}.files
%defattr(0644,root,root,0755)
%doc ACKNOWLEDGEMENTS AUTHORS COPYING INSTALL NEWS README
%defattr(-,root,root,0755)
%dir %{_jvmdir}/%{sdkdir}
%dir %{jvmjardir}
%{jvmjardir}/*.jar
%{_jvmdir}/%{jrelnk}
%{_jvmjardir}/%{jrelnk}
%{_bindir}/%{origin}
%{_datadir}/%{origin}
%{_libdir}


%changelog
* Tue Feb 21 2012 Jon Dill <dillj@mandriva.org> 0:1.5.3-3mdv2012.0
+ Revision: 778765
- rebuild against new version of libffi4

* Fri Dec 10 2010 Oden Eriksson <oeriksson@mandriva.com> 0:1.5.3-2mdv2011.0
+ Revision: 619779
- the mass rebuild of 2010.0 packages

* Mon Aug 03 2009 Frederik Himpe <fhimpe@mandriva.org> 0:1.5.3-1mdv2010.0
+ Revision: 408493
- Update to new version 1.5.3

* Thu Aug 07 2008 Thierry Vignaud <tv@mandriva.org> 0:1.5.1-2mdv2009.0
+ Revision: 267207
- rebuild early 2009.0 package (before pixel changes)

* Tue Apr 15 2008 Alexander Kurtakov <akurtakov@mandriva.org> 0:1.5.1-1mdv2009.0
+ Revision: 194102
- new version

* Mon Jan 28 2008 David Walluck <walluck@mandriva.org> 0:1.5.0-1mdv2008.1
+ Revision: 159484
- 1.5.0

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request

* Sun Dec 16 2007 Anssi Hannula <anssi@mandriva.org> 0:1.4.5-8mdv2008.1
+ Revision: 120923
- buildrequire java-rpmbuild, i.e. build with icedtea on x86(_64)

* Sat Jul 21 2007 David Walluck <walluck@mandriva.org> 0:1.4.5-7mdv2008.0
+ Revision: 54198
- remove gcj-tools requirement
- fix build

* Sat Jul 21 2007 David Walluck <walluck@mandriva.org> 0:1.4.5-6mdv2008.0
+ Revision: 54176
- fix jsse link
- 1.5.0, not 1.4.2
- %%{jrelnk}/bin not %%{jredir}/bin

* Sun Jul 01 2007 Anssi Hannula <anssi@mandriva.org> 0:1.4.5-4mdv2008.0
+ Revision: 46809
- build with ffi on all archs, fixes crash on non-x86_64


* Wed Mar 14 2007 Frederic Crozat <fcrozat@mandriva.com> 1.4.5-2mdv2007.1
+ Revision: 143653
- Fix update-alternative uninstall (diagnosed by pixel)

  + Thierry Vignaud <tvignaud@mandriva.com>
    - do not package empty ChangeLog

* Wed Feb 14 2007 David Walluck <walluck@mandriva.org> 0:1.4.5-1mdv2007.1
+ Revision: 121154
- 1.4.5

* Fri Dec 15 2006 David Walluck <walluck@mandriva.org> 0:1.4.4-2mdv2007.1
+ Revision: 97248
- change priority to be less than gcj

* Thu Nov 09 2006 David Walluck <walluck@mandriva.org> 0:1.4.4-1mdv2007.1
+ Revision: 79927
- 1.4.4
- BuildRequires: libffi-devel on x86_64
- Import jamvm

* Tue Sep 05 2006 David Walluck <walluck@mandriva.org> 0:1.4.3-3mdv2007.0
- ExcludeArch: sparc

* Thu Jun 15 2006 David Walluck <walluck@mandriva.org> 0:1.4.3-2mdv2007.0
- fix BuildRequires

* Thu Jun 01 2006 David Walluck <walluck@mandriva.org> 0:1.4.3-1mdv2007.0
- rebuild for libgcj.so.7
- remove gnu-crypto and jessie dependencies

* Wed Apr 26 2006 David Walluck <walluck@mandriva.org> 0:1.4.2-4mdk
- set empty CLASSPATH
- but back fix for lib directory

* Thu Apr 13 2006 David Walluck <walluck@mandriva.org> 0:1.4.2-3mdk
- CVS 20060411

* Tue Feb 21 2006 David Walluck <walluck@mandriva.org> 0:1.4.2-2mdk
- rebuild on x86_64

* Tue Jan 31 2006 David Walluck <walluck@mandriva.org> 0:1.4.2-1mdk
- 1.4.2

* Sat Jan 14 2006 David Walluck <walluck@mandriva.org> 0:1.4.1-2mdk
- add java and rmiregistry symlinks

* Fri Jan 13 2006 David Walluck <walluck@mandriva.org> 0:1.4.1-1mdk
- 1.4.1
- change name to jamvm

* Fri Nov 04 2005 David Walluck <walluck@mandriva.org> 0:1.4.2.0-0.0.1mdk
- release

