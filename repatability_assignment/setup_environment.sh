#!/bin/sh

package_check(){
    pack=$(2>>/dev/null pacman -Q $1) 
    if [[ "" == $pack ]]; then
        echo "package" $1 "not found"   
    fi
}

package_check wget
package_check python
package_check python-pip


wget "https://github.com/davidebreso/pynusmv/releases/download/v1.0rc8-2023/pynusmv-1.0rc8-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl"

while [[ -n `ps | grep wget` ]]; do
  sleep 0.05; echo -n '.'                 ## do something while waiting
done

python -m venv ./venv

./venv/bin/pip install pynusmv-1.0rc8-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl


echo "testing"
./venv/bin/python react_mc.py react_examples/gigamax.smv
rm pynusmv-1.0rc8-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl



