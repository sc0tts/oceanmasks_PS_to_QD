"""combine_ocean_masks.py

Combine the oisst qd water mask
with the qd water masks from polarstereo
"""

import numpy as np
import imageio



def combine_masks():
    """Combine the masks"""
    fn_psn25 = './watermask_psn25_on_qd.tif'
    fn_pss25 = './watermask_pss25_on_qd.tif'
    #fn_oisst = './oisst_water.dat'
    fn_oisst = './watermask_oisst_on_qd.tif'

    arr_psn25 = np.array(imageio.read(fn_psn25).get_data(0))
    arr_pss25 = np.array(imageio.read(fn_pss25).get_data(0))
    arr_oisst = np.array(imageio.read(fn_oisst).get_data(0))

    combined = np.zeros(arr_oisst.shape, dtype=np.uint8)
    combined[arr_oisst > 0] += 100

    combined[arr_psn25 > 0] += 150
    combined[arr_pss25 > 0] += 150

    fn_combined_mask = 'combined_ocean_masks.dat'
    combined.tofile(fn_combined_mask)
    print('Read in:')
    print(f'  {fn_psn25=}')
    print(f'  {fn_pss25=}')
    print(f'  {fn_oisst=}')
    print('Wrote:')
    print(f'  {fn_combined_mask}')


if __name__ == '__main__':
    combine_masks()
