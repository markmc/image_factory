version:
	git describe > version.txt
	perl -p -i -e 's/-/_/g' version.txt

sdist:
	python setup.py sdist

signed-rpm: sdist version
	rpmbuild -ba imagefactory.spec --sign --define "_sourcedir `pwd`/dist"i

rpm: sdist version
	rpmbuild -ba imagefactory.spec --define "_sourcedir `pwd`/dist"

srpm: sdist version
	rpmbuild -bs imagefactory.spec --define "_sourcedir `pwd`/dist"

clean:
	rm -rf MANIFEST build dist imagefactory.spec version.txt
