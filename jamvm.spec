%define origin          jamvm
%define originver       %{version}

%define _libdir         %{_prefix}/%{_lib}/%{origin}

%define priority        1410
%define javaver         1.5.0
%define buildver        0

%define _jvmdir		%{_prefix}/lib/jvm
%define _jvmjardir	%{_datadir}/java

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
Version:        2.0.0
Release:        1
Summary:        Old but small JVM
Group:          Development/Java
License:        GPL
URL:            http://jamvm.sourceforge.net/
Source0:        https://altushost-swe.dl.sourceforge.net/project/jamvm/jamvm/JamVM%20%{version}/jamvm-%{version}.tar.gz
BuildRequires:  jikes
BuildRequires:  pkgconfig(libffi)
Provides:       java-%{javaver}-%{origin} = %{EVRD}

%description
JamVM is an old and unmaintained, but small, implementation of a
Java Virtual Machine.

Since it can build without a preexisting JVM, its primary use is
bootstrapping the newer OpenJDK JVMs.

%prep
%autosetup -p1 -n %{origin}-%{originver}
%{__perl} -pi -e 's|lib/classpath|%{_lib}/classpath|' src/classlib/gnuclasspath/dll.c

%build
export CLASSPATH=
export JAVAC=%{_bindir}/jikes
export JAR=%{_bindir}/fastjar
%configure \
	--enable-ffi \
	--with-classpath-install-dir=%{_prefix}
%make_build

%install
%make_install

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
popd

pushd $RPM_BUILD_ROOT%{_jvmjardir}
	ln -s %{sdkdir} %{jrelnk}
popd

for i in rt jaas jdbc-stdext jndi jaxp_parser_impl jaxp_transform_impl; do
	ln -s %{_datadir}/classpath/glibj.zip %{buildroot}%{_jvmdir}/%{cname}-%{java_version}/jre/lib/$i.jar
done

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
