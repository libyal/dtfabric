#!/bin/bash
#
# Script to set up Travis-CI test VM.
#
# This file is generated by l2tdevtools update-dependencies.py any dependency
# related changes should be made in dependencies.ini.

L2TBINARIES_DEPENDENCIES="PyYAML";

L2TBINARIES_TEST_DEPENDENCIES="funcsigs mock pbr six";

DPKG_PYTHON2_DEPENDENCIES="python-yaml";

DPKG_PYTHON2_TEST_DEPENDENCIES="python-coverage python-funcsigs python-mock python-pbr python-six";

DPKG_PYTHON3_DEPENDENCIES="python3-yaml";

DPKG_PYTHON3_TEST_DEPENDENCIES="python3-mock python3-pbr python3-setuptools python3-six";

RPM_PYTHON2_DEPENDENCIES="python2-pyyaml";

RPM_PYTHON2_TEST_DEPENDENCIES="python2-funcsigs python2-mock python2-pbr python2-six";

RPM_PYTHON3_DEPENDENCIES="python3-pyyaml";

RPM_PYTHON3_TEST_DEPENDENCIES="python3-mock python3-pbr python3-six";

# Exit on error.
set -e;

if test ${TRAVIS_OS_NAME} = "osx";
then
	git clone https://github.com/log2timeline/l2tbinaries.git -b dev;

	mv l2tbinaries ../;

	for PACKAGE in ${L2TBINARIES_DEPENDENCIES};
	do
		echo "Installing: ${PACKAGE}";
		sudo /usr/bin/hdiutil attach ../l2tbinaries/macos/${PACKAGE}-*.dmg;
		sudo /usr/sbin/installer -target / -pkg /Volumes/${PACKAGE}-*.pkg/${PACKAGE}-*.pkg;
		sudo /usr/bin/hdiutil detach /Volumes/${PACKAGE}-*.pkg
	done

	for PACKAGE in ${L2TBINARIES_TEST_DEPENDENCIES};
	do
		echo "Installing: ${PACKAGE}";
		sudo /usr/bin/hdiutil attach ../l2tbinaries/macos/${PACKAGE}-*.dmg;
		sudo /usr/sbin/installer -target / -pkg /Volumes/${PACKAGE}-*.pkg/${PACKAGE}-*.pkg;
		sudo /usr/bin/hdiutil detach /Volumes/${PACKAGE}-*.pkg
	done

elif test -n "${FEDORA_VERSION}";
then
	CONTAINER_NAME="fedora${FEDORA_VERSION}";

	docker pull registry.fedoraproject.org/fedora:${FEDORA_VERSION};

	docker run --name=${CONTAINER_NAME} --detach -i registry.fedoraproject.org/fedora:${FEDORA_VERSION};

	docker exec ${CONTAINER_NAME} dnf install -y dnf-plugins-core;

	docker exec ${CONTAINER_NAME} dnf copr -y enable @gift/dev;

	if test -n "${TOXENV}";
	then
		docker exec ${CONTAINER_NAME} dnf install -y python3-tox;

	elif test ${TRAVIS_PYTHON_VERSION} = "2.7";
	then
		docker exec ${CONTAINER_NAME} dnf install -y git python2 ${RPM_PYTHON2_DEPENDENCIES} ${RPM_PYTHON2_TEST_DEPENDENCIES};
	else
		docker exec ${CONTAINER_NAME} dnf install -y git python3 ${RPM_PYTHON3_DEPENDENCIES} ${RPM_PYTHON3_TEST_DEPENDENCIES};
	fi

	docker cp ../dtfabric ${CONTAINER_NAME}:/

elif test -n "${UBUNTU_VERSION}";
then
	CONTAINER_NAME="ubuntu${UBUNTU_VERSION}";

	docker pull ubuntu:${UBUNTU_VERSION};

	docker run --name=${CONTAINER_NAME} --detach -i ubuntu:${UBUNTU_VERSION};

	docker exec ${CONTAINER_NAME} apt-get update -q;
	docker exec ${CONTAINER_NAME} sh -c "DEBIAN_FRONTEND=noninteractive apt-get install -y software-properties-common";

	docker exec ${CONTAINER_NAME} add-apt-repository ppa:gift/dev -y;

	if test -n "${TOXENV}";
	then
		docker exec ${CONTAINER_NAME} add-apt-repository universe;
		docker exec ${CONTAINER_NAME} add-apt-repository ppa:deadsnakes/ppa -y;

		DPKG_PYTHON="python${TRAVIS_PYTHON_VERSION} python${TRAVIS_PYTHON_VERSION}-dev";

		docker exec ${CONTAINER_NAME} sh -c "DEBIAN_FRONTEND=noninteractive apt-get install -y locales build-essential ${DPKG_PYTHON} tox";

	elif test ${TRAVIS_PYTHON_VERSION} = "2.7";
	then
		docker exec ${CONTAINER_NAME} sh -c "DEBIAN_FRONTEND=noninteractive apt-get install -y git python ${DPKG_PYTHON2_DEPENDENCIES} ${DPKG_PYTHON2_TEST_DEPENDENCIES}";
	else
		docker exec ${CONTAINER_NAME} sh -c "DEBIAN_FRONTEND=noninteractive apt-get install -y git python3 ${DPKG_PYTHON3_DEPENDENCIES} ${DPKG_PYTHON3_TEST_DEPENDENCIES}";
	fi

	docker cp ../dtfabric ${CONTAINER_NAME}:/

elif test ${TRAVIS_OS_NAME} = "linux" && test ${TARGET} != "jenkins";
then
	sudo rm -f /etc/apt/sources.list.d/travis_ci_zeromq3-source.list;

	if test ${TARGET} = "pylint";
	then
		sudo add-apt-repository ppa:gift/pylint3 -y;
	fi

	sudo add-apt-repository ppa:gift/dev -y;
	sudo apt-get update -q;

	if test ${TRAVIS_PYTHON_VERSION} = "2.7";
	then
		sudo apt-get install -y ${DPKG_PYTHON2_DEPENDENCIES} ${DPKG_PYTHON2_TEST_DEPENDENCIES};
	else
		sudo apt-get install -y ${DPKG_PYTHON3_DEPENDENCIES} ${DPKG_PYTHON3_TEST_DEPENDENCIES};
	fi
	if test ${TARGET} = "pylint";
	then
		sudo apt-get install -y pylint;
	fi
fi
