from conans import ConanFile, tools, MSBuild
from conanos.build import config_scheme
import os, shutil, sys

class LibrsvgConan(ConanFile):
    name = "librsvg"
    version = "2.40.20"
    description = "librsvg is a library to render SVG files using cairo."
    url = "https://github.com/conanos/librsvg"
    homepage = "https://wiki.gnome.org/action/show/Projects/LibRsvg"
    license = "GPL-v2"
    exports = ["COPYING","librsvg.sln","rsvg-install.vcxproj","rsvg-install.props"]
    generators = "visual_studio", "gcc"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = { 'shared': True, 'fPIC': True }

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    #requires = ("libcroco/0.6.12@conanos/dev", "gdk-pixbuf/2.36.2@conanos/dev", "vala-m4/0.35.2@conanos/dev",
    #"gobject-introspection-m4/1.58.0@conanos/dev", "pango/1.40.14@conanos/dev", "cairo/1.14.12@conanos/dev",
    #
    #"libpng/1.6.34@conanos/dev","libxml2/2.9.8@conanos/dev","pixman/0.34.0@conanos/dev",
    #"fontconfig/2.12.6@conanos/dev","freetype/2.9.0@conanos/dev","harfbuzz/1.7.5@conanos/dev",
    #"gobject-introspection/1.58.0@conanos/dev", "glib/2.58.0@conanos/dev", "libffi/3.3-rc0@conanos/dev"
    #)
    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx

        config_scheme(self)

    def requirements(self):
        self.requires.add("libcroco/0.6.12@conanos/stable")
        self.requires.add("gdk-pixbuf/2.38.0@conanos/stable")
        self.requires.add("pango/1.42.4@conanos/stable")
        self.requires.add("cairo/1.15.12@conanos/stable")

    def build_requirements(self):
        if self.settings.os == 'Windows':
            self.build_requires("7z_installer/1.0@conan/stable")
            self.build_requires("glib/2.58.1@conanos/stable")

    def source(self):
        maj_ver = '.'.join(self.version.split('.')[0:2])
        tarball_name = 'librsvg-{version}.tar'.format(version=self.version)
        archive_name = '%s.xz' % tarball_name
        url_ = 'http://ftp.gnome.org/pub/GNOME/sources/librsvg/{maj_ver}/{archive_name}'
        tools.download(url_.format(maj_ver=maj_ver,archive_name=archive_name), archive_name)
        
        if self.settings.os == 'Windows':
            self.run('7z x %s' % archive_name)
            self.run('7z x %s' % tarball_name)
            os.unlink(tarball_name)
        else:
            self.run('tar -xJf %s' % archive_name)
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)
        os.unlink(archive_name)

    def build(self):
        #with tools.chdir(self.source_subfolder):
        #    with tools.environment_append({
        #        'PKG_CONFIG_PATH' : '%s/lib/pkgconfig:%s/lib/pkgconfig:%s/lib/pkgconfig:%s/lib/pkgconfig'
        #        ':%s/lib/pkgconfig:%s/lib/pkgconfig:%s/lib/pkgconfig:%s/lib/pkgconfig'
        #        ':%s/lib/pkgconfig:%s/lib/pkgconfig:%s/lib/pkgconfig:%s/lib/pkgconfig:%s/lib/pkgconfig'
        #        %(self.deps_cpp_info["libcroco"].rootpath,self.deps_cpp_info["gdk-pixbuf"].rootpath,
        #        self.deps_cpp_info["pango"].rootpath,self.deps_cpp_info["cairo"].rootpath,
        #        self.deps_cpp_info["libpng"].rootpath,self.deps_cpp_info["libxml2"].rootpath,
        #        self.deps_cpp_info["pixman"].rootpath,self.deps_cpp_info["fontconfig"].rootpath,
        #        self.deps_cpp_info["freetype"].rootpath,self.deps_cpp_info["harfbuzz"].rootpath,
        #        self.deps_cpp_info["gobject-introspection"].rootpath,self.deps_cpp_info["glib"].rootpath,
        #        self.deps_cpp_info["libffi"].rootpath,),
        #        'LD_LIBRARY_PATH' : '%s/lib:%s/lib'%(self.deps_cpp_info["libffi"].rootpath,self.deps_cpp_info["glib"].rootpath),
        #        'XDG_DATA_DIRS' : ":%s/share/:$XDG_DATA_DIRS"%(self.deps_cpp_info["gdk-pixbuf"].rootpath),
        #        'C_INCLUDE_PATH' : "{glib_root}/include/glib-2.0:{glib_root}/lib/glib-2.0/include"
        #        ":{gdk_root}/include/gdk-pixbuf-2.0:{cairo_root}/include/cairo".format(glib_root=self.deps_cpp_info["glib"].rootpath,
        #        gdk_root=self.deps_cpp_info["gdk-pixbuf"].rootpath,cairo_root=self.deps_cpp_info["cairo"].rootpath)
        #        }):

        #        self.run('mkdir -p m4 && autoreconf -fiv')

        #        _args = ["--prefix=%s/builddir"%(os.getcwd()), "--disable-pixbuf-loader", "--without-gtk3",
        #        "--enable-introspection"]
        #        if self.options.shared:
        #            _args.extend(['--enable-shared=yes','--enable-static=no'])
        #        else:
        #            _args.extend(['--enable-shared=no','--enable-static=yes'])

        #        self.run("./configure %s"%(' '.join(_args)))
        #        self.run("make -j4")
        #        self.run("make install")
        if self.settings.os == 'Windows':
            for i in ["librsvg.sln","rsvg-install.vcxproj","rsvg-install.props"]:
                shutil.copy2(os.path.join(self.build_folder,i), os.path.join(self.build_folder,self._source_subfolder,"build","win32","vs15"))
            with tools.chdir(os.path.join(self._source_subfolder,"build","win32","vs15")):
                replacements = {
                    "$(GlibEtcInstallRoot)\include\cairo" : os.path.join(self.deps_cpp_info["cairo"].rootpath, "include", "cairo"),
                    "$(GlibEtcInstallRoot)\include\gdk-pixbuf-2.0" : os.path.join(self.deps_cpp_info["gdk-pixbuf"].rootpath, "include", "gdk-pixbuf-2.0"),
                    "$(GlibEtcInstallRoot)\include\pango-1.0" :  os.path.join(self.deps_cpp_info["pango"].rootpath, "include", "pango-1.0"),
                    "$(GlibEtcInstallRoot)\include\libcroco-0.6" : os.path.join(self.deps_cpp_info["libcroco"].rootpath, "include", "libcroco-0.6"),
                    "$(GlibEtcInstallRoot)\include\gio-win32-2.0" : os.path.join(self.deps_cpp_info["glib"].rootpath, "include", "gio-win32-2.0"),
                }
                for s, r in replacements.items():
                    tools.replace_in_file("rsvg-build-defines.props",s,r,strict=True)
                #replacements_install = {
                #    "$(GlibEtcInstallRoot)" : os.path.join(self.deps_cpp_info["gdk-pixbuf"].rootpath),
                #}
                #for s, r in replacements_install.items():
                #    tools.replace_in_file("rsvg-install.props",s,r,strict=True)
                replacements_path = {
                     "<PythonDirX64>$(PythonDir).x64</PythonDirX64>" : "<PythonDirX64>%s</PythonDirX64>"%(os.path.dirname(sys.executable))
                }
                for s, r in replacements_path.items():
                    tools.replace_in_file("rsvg-version-paths.props",s,r,strict=True)
                msbuild = MSBuild(self)
                msbuild.build("librsvg.sln",upgrade_project=True,platforms={'x86': 'Win32', 'x86_64': 'x64'})

    def package(self):
        if self.settings.os == 'Windows':
            platforms = {'x86': 'Win32', 'x86_64': 'x64'}
            output_rpath = os.path.join("vs15",platforms.get(str(self.settings.arch)))
            self.copy("*", dst=os.path.join(self.package_folder),src=os.path.join(self.build_folder,output_rpath))
        #if tools.os_info.is_linux:
        #    with tools.chdir(self.source_subfolder):
        #        self.copy("*", src="%s/builddir"%(os.getcwd()))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)