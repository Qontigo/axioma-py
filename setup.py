"""
Copyright © 2022 Qontigo GmbH.
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied.  See the License for the
specific language governing permissions and limitations
under the License.

"""
import setuptools
import versioneer

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="axiomapy",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    author="Qontigo",
    author_email="axioma-py@qontigo.com",
    description="Ideas for an api toolkit package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "pandas",
        "httpx>=0.16.0",
        "typing;python_version<'3.7'",
        "typing-inspect",
        "inflection",
        "contextvars;python_version<'3.7'",
        "backoff",
        "requests"
    ],
    extras_require={
        "notebook": ["jupyter"],
        "test": [
            "pytest",
            "pytest-cov",
            "pytest-mock",
            "testfixtures",
            "nbconvert",
            "nbformat",
            "jupyter_client",
        ],
        "develop": [
            "wheel",
            "sphinx",
            "sphinx_rtd_theme",
            "sphinx_autodoc_typehints",
            "sphinx_copybutton",
            "pre-commit",
            "nbconvert",
            "nbformat",
            "nbsphinx",
            "flake8",
            "black",
            "sphinx_toolbox",
            "enum_tools"
        ],
    },
)
