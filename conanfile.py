from conans import ConanFile, CMake, tools
import os

class LibrsvgConan(ConanFile):
    name = "librsvg"
    version = "2.40.20"
    description = "librsvg is a library to render SVG files using cairo."
    url = "https://github.com/conan-multimedia/librsvg"
    wiki = "https://wiki.gnome.org/Projects/LibRsvg"
    license = "LGPLv2"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = "shared=True"
    generators = "cmake"

    requires = ("libcroco/0.6.12@conanos/dev", "gdk-pixbuf/2.36.2@conanos/dev", "vala-m4/0.35.2@conanos/dev",
    "gobject-introspection-m4/1.58.0@conanos/dev", "pango/1.40.14@conanos/dev", "cairo/1.14.12@conanos/dev",
    
    "libpng/1.6.34@conanos/dev","libxml2/2.9.8@conanos/dev","pixman/0.34.0@conanos/dev",
    "fontconfig/2.12.6@conanos/dev","freetype/2.9.0@conanos/dev","harfbuzz/1.7.5@conanos/dev",
    "gobject-introspection/1.58.0@conanos/dev", "glib/2.58.0@conanos/dev", "libffi/3.3-rc0@conanos/dev"
    )

    source_subfolder = "source_subfolder"

    def source(self):
        maj_ver = '.'.join(self.version.split('.')[0:2])
        tarball_name = '{name}-{version}.tar'.format(name=self.name, version=self.version)
        archive_name = '%s.xz' % tarball_name
        url_ = 'http://ftp.acc.umu.se/pub/GNOME/sources/{name}/{major_version}/{archive_name}'.format(name=self.name,major_version=maj_ver, archive_name=archive_name)
        tools.download(url_, archive_name)

        if self.settings.os == 'Windows':
            self.run('7z x %s' % archive_name)
            self.run('7z x %s' % tarball_name)
            os.unlink(tarball_name)
        else:
            self.run('tar -xJf %s' % archive_name)
        os.rename('%s-%s'%(self.name,self.version) , self.source_subfolder)
        os.unlink(archive_name)

    def build(self):
        with tools.chdir(self.source_subfolder):
            with tools.environment_append({
                'PKG_CONFIG_PATH' : '%s/lib/pkgconfig:%s/lib/pkgconfig:%s/lib/pkgconfig:%s/lib/pkgconfig'
                ':%s/lib/pkgconfig:%s/lib/pkgconfig:%s/lib/pkgconfig:%s/lib/pkgconfig'
                ':%s/lib/pkgconfig:%s/lib/pkgconfig:%s/lib/pkgconfig:%s/lib/pkgconfig:%s/lib/pkgconfig'
                %(self.deps_cpp_info["libcroco"].rootpath,self.deps_cpp_info["gdk-pixbuf"].rootpath,
                self.deps_cpp_info["pango"].rootpath,self.deps_cpp_info["cairo"].rootpath,
                self.deps_cpp_info["libpng"].rootpath,self.deps_cpp_info["libxml2"].rootpath,
                self.deps_cpp_info["pixman"].rootpath,self.deps_cpp_info["fontconfig"].rootpath,
                self.deps_cpp_info["freetype"].rootpath,self.deps_cpp_info["harfbuzz"].rootpath,
                self.deps_cpp_info["gobject-introspection"].rootpath,self.deps_cpp_info["glib"].rootpath,
                self.deps_cpp_info["libffi"].rootpath,),
                'LD_LIBRARY_PATH' : '%s/lib:%s/lib'%(self.deps_cpp_info["libffi"].rootpath,self.deps_cpp_info["glib"].rootpath),
                'XDG_DATA_DIRS' : ":%s/share/:$XDG_DATA_DIRS"%(self.deps_cpp_info["gdk-pixbuf"].rootpath),
                'C_INCLUDE_PATH' : "{glib_root}/include/glib-2.0:{glib_root}/lib/glib-2.0/include"
                ":{gdk_root}/include/gdk-pixbuf-2.0:{cairo_root}/include/cairo".format(glib_root=self.deps_cpp_info["glib"].rootpath,
                gdk_root=self.deps_cpp_info["gdk-pixbuf"].rootpath,cairo_root=self.deps_cpp_info["cairo"].rootpath)
                }):

                self.run('mkdir -p m4 && autoreconf -fiv')

                _args = ["--prefix=%s/builddir"%(os.getcwd()), "--disable-pixbuf-loader", "--without-gtk3",
                "--enable-introspection"]
                if self.options.shared:
                    _args.extend(['--enable-shared=yes','--enable-static=no'])
                else:
                    _args.extend(['--enable-shared=no','--enable-static=yes'])

                self.run("./configure %s"%(' '.join(_args)))
                self.run("make -j4")
                self.run("make install")

    def package(self):
        if tools.os_info.is_linux:
            with tools.chdir(self.source_subfolder):
                self.copy("*", src="%s/builddir"%(os.getcwd()))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)