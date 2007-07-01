%define origin          jamvm
%define version         1.4.5
%define originver       %{version}

%define _libdir         %{_prefix}/%{_lib}/%{name}

%define section         free

%define priority        1410
%define javaver         1.4.2
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
Version:        %{originver}
Release:        %mkrel 3
Epoch:          0
Summary:        Java Virtual Machine which conforms to the JVM specification version 2
Group:          Development/Java
License:        GPL
URL:            http://jamvm.sourceforge.net/
Source0:        http://superb-east.dl.sourceforge.net/jamvm/jamvm-%{originver}.tar.bz2
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root
BuildRequires:  java-devel
BuildRequires:  jpackage-utils >= 0:1.5
BuildRequires:  ffi-devel
Requires:       gcj-tools
Requires(post): classpath >= 0:0.19
Requires(postun): classpath >= 0:0.19
Requires(post): jpackage-utils >= 0:1.6.3
Requires(postun): jpackage-utils >= 0:1.6.3
Requires(post): gcj-tools
Requires(postun): gcj-tools
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
%configure2_5x \
  --enable-ffi \
  --with-classpath-install-dir=%{_prefix}
%make

%install
rm -rf %{buildroot}
%makeinstall

%{__mkdir_p} $RPM_BUILD_ROOT%{_jvmdir}/%{jredir}/bin
(cd $RPM_BUILD_ROOT%{_jvmdir}/%{jredir}/bin \
 && %{__ln_s} %{_bindir}/%{origin} java \
 && %{__ln_s} %{_bindir}/grmiregistry rmiregistry)

%{__mkdir_p} $RPM_BUILD_ROOT%{_jvmdir}/%{jredir}/lib

# create extensions symlinks
# jessie
ln -s %{_javadir}/jsse.jar $RPM_BUILD_ROOT%{_jvmdir}/%{jredir}/lib/jsse.jar

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

%clean
rm -rf %{buildroot}

%post
update-alternatives \
  --install %{_bindir}/java java %{_jvmdir}/%{jredir}/bin/java %{priority} \
  --slave %{_jvmdir}/jre          jre          %{_jvmdir}/%{jrelnk} \
  --slave %{_jvmjardir}/jre       jre_exports  %{_jvmjardir}/%{jrelnk} \
  --slave %{_bindir}/rmiregistry  rmiregistry  %{_jvmdir}/%{jredir}/bin/rmiregistry

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
   update-alternatives --remove java %{_jvmdir}/%{jredir}/bin/java 
   update-alternatives --remove jre_%{origin}  %{_jvmdir}/%{jrelnk}
   update-alternatives --remove jre_%{javaver} %{_jvmdir}/%{jrelnk}
   update-alternatives --remove jaxp_parser_impl \
     %{_datadir}/classpath/glibj.zip
   update-alternatives --remove jaxp_transform_impl \
     %{_datadir}/classpath/glibj.zip
fi

%files -f %{name}-%{version}.files
%defattr(-,root,root,-)
%doc ACKNOWLEDGEMENTS AUTHORS COPYING INSTALL NEWS README
%dir %{_jvmdir}/%{sdkdir}
%dir %{jvmjardir}
%{jvmjardir}/*.jar
%{_jvmdir}/%{jrelnk}
%{_jvmjardir}/%{jrelnk}
%{_bindir}/%{origin}
%{_datadir}/%{origin}
%{_prefix}/%{_lib}/%{name}/libjvm.*


