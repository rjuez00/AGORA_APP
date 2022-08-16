@echo off

rmdir Executable /s /q 
rmdir Output /s /q 

mkdir Executable
cd Executable



pyinstaller --onedir --noconsole --add-data="../../auxFiles/*;auxFiles" --icon="../../auxFiles/appLogo.ico" --hidden-import=tqdm  --hidden-import="pkg_resources.py2_warn" --hidden-import="googleapiclient" --hidden-import="apiclient" --hidden-import=tensorflow --hidden-import=pytorch --collect-data tensorflow --collect-data torch --copy-metadata tensorflow --copy-metadata torch --copy-metadata tqdm --copy-metadata regex --copy-metadata sacremoses --copy-metadata requests --copy-metadata packaging --copy-metadata filelock --copy-metadata numpy --copy-metadata tokenizers --copy-metadata importlib_metadata --hidden-import="sklearn.utils._cython_blas" --hidden-import="sklearn.neighbors.typedefs" --hidden-import="sklearn.neighbors.quad_tree" --hidden-import="sklearn.tree._utils" --hidden-import="sklearn.utils._typedefs" --hidden-import="sklearn.neighbors._partition_nodes" ../../AGORA.py


: Xcopy ..\..\auxFiles dist\auxFiles /I

cd ..


iscc installator_generator.iss