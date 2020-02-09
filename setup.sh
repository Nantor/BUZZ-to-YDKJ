#!/bin/bash

# force to run as root
if [ "$(id -u)" != "0" ]; then
  sudo "$0" "$@"
  exit $?
fi

# initial Parameter:
# Buzz controller device default properteis
VENDOR_ID=054C
PRODUCT_ID=1000

# install dependencies
apt update
apt install python3-pip libhidapi-hidraw0
pip3 install hid keyboard

# detect Buzz controller
LSUSB=$(lsusb)
if ! (echo "$LSUSB" | grep -iq "$VENDOR_ID:$PRODUCT_ID"); then
  __BUZZ_COUNT=$(echo "$LSUSB" | grep -ci "buzz")
  if [ "$__BUZZ_COUNT" = "1" ]; then
    __BUZZ_DEV=$(echo "$LSUSB" | grep -i "buzz")
    VENDOR_ID=$(echo "$__BUZZ_DEV" | cut -c24-27)
    PRODUCT_ID=$(echo "$__BUZZ_DEV" | cut -c29-33)
  else
    __COUNT=$(echo "$LSUSB" | wc -l)
    while :; do
      echo "No Buzz Controller found, please choose: "
      echo "     0)  abort and exit"
      echo "$LSUSB" | cut -c34- | nl -s')  '
      read -r __SELECT
      if [[ ! "$__SELECT" =~ [^0-9] ]] && [[ $__SELECT -le $__COUNT ]]; then
        if [[ $__SELECT -eq 0 ]]; then
          exit 1
        fi
        __SELECTED=$(echo "$LSUSB" | sed "${__SELECT}q;d")
        VENDOR_ID=$(echo "$__SELECTED" | cut -c24-27)
        PRODUCT_ID=$(echo "$__SELECTED" | cut -c29-33)
        break
      fi
    done
  fi
fi

cat >buzz.json <<EOF
{"controller":{"vendor_id":$((16#$VENDOR_ID)),"product_id":$((16#$PRODUCT_ID))}}
EOF
