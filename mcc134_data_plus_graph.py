#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from time import sleep
from sys import stdout
from daqhats import mcc134, HatIDs, HatError, TcTypes
from daqhats_utils import select_hat_device, tc_type_to_string
import pandas as pd
import os

# Constants
CURSOR_BACK_2 = '\x1b[2D'
ERASE_TO_END_OF_LINE = '\x1b[0K'
RECORD_BLOCK_SIZE = 15  # 15 records per block
MAX_RECORDS = 60 * 60 * 3  # 3 hours at 1 record per second
FILE_NAME = "temperature_data.csv"


def main():
    tc_type = TcTypes.TYPE_E   # change this to the desired thermocouple type
    delay_between_reads = 1  # Seconds
    channels = (0, )

    # DataFrame to hold the data
    df = pd.DataFrame()

    try:
        address = select_hat_device(HatIDs.MCC_134)
        hat = mcc134(address)

        for channel in channels:
            hat.tc_type_write(channel, tc_type)

        print('\nMCC 134 single data value read example')
        print('    Function demonstrated: mcc134.t_in_read')
        print('    Channels: ' + ', '.join(str(channel) for channel in channels))
        print('    Thermocouple type: ' + tc_type_to_string(tc_type))
        try:
            input("\nPress 'Enter' to continue")
        except (NameError, SyntaxError):
            pass

        print('\nAcquiring data ... Press Ctrl-C to abort')

        print('\n  Sample', end='')
        for channel in channels:
            print('     Channel', channel, end='')
        print('')

        try:
            samples_per_channel = 0
            while samples_per_channel < MAX_RECORDS:
                row_data = {'Sample': samples_per_channel}

                print('\r{:8d}'.format(samples_per_channel), end='')

                for channel in channels:
                    value = hat.t_in_read(channel)
                    if value == mcc134.OPEN_TC_VALUE:
                        print('     Open     ', end='')
                        row_data[f'Channel {channel}'] = 'Open'
                    elif value == mcc134.OVERRANGE_TC_VALUE:
                        print('     OverRange', end='')
                        row_data[f'Channel {channel}'] = 'OverRange'
                    elif value == mcc134.COMMON_MODE_TC_VALUE:
                        print('   Common Mode', end='')
                        row_data[f'Channel {channel}'] = 'Common Mode'
                    else:
                        print('{:12.2f} C'.format(value), end='')
                        row_data[f'Channel {channel}'] = value

                df = df.append(row_data, ignore_index=True)

                stdout.flush()

                # Save to .csv file and clear DataFrame every RECORD_BLOCK_SIZE records
                if samples_per_channel % RECORD_BLOCK_SIZE == 0 and not df.empty:
                    if os.path.isfile(FILE_NAME):
                        df.to_csv(FILE_NAME, mode='a', header=False)
                    else:
                        df.to_csv(FILE_NAME, mode='w', header=True)

                    df = pd.DataFrame()  # Reset the DataFrame

                sleep(delay_between_reads)
                samples_per_channel += 1

        except KeyboardInterrupt:
            print(CURSOR_BACK_2, ERASE_TO_END_OF_LINE, '\n')

    except (HatError, ValueError) as error:
        print('\n', error)


if __name__ == '__main__':
    main()
