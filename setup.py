"""Installation script."""
import setuptools

setuptools.setup(
	name="Arthropod",
	tests_require=["pytest", "pytest-cov", "hypothesis"],
	install_requires=["gensim"])