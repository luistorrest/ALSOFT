# imageProcess.py

import cv2
import numpy as np
from math import factorial

# Define global variables
corto_pixeles = None  # Threshold for short cuttings in pixels
largo_pixeles = None  # Threshold for long cuttings in pixels
hojabase_pixeles = None  # Threshold for base leaf in pixels
factor = None  # Conversion factor from pixels to centimeters

def set_global_variables(corto_pix, largo_pix, hojabase_pix, conversion_factor):
    """Set the global variables for the module.
    
    Args:
        corto_pix: Threshold for short cuttings in pixels.
        largo_pix: Threshold for long cuttings in pixels.
        hojabase_pix: Threshold for base leaf in pixels.
        conversion_factor: Conversion factor from pixels to centimeters.
    """
    global corto_pixeles, largo_pixeles, hojabase_pixeles, factor
    corto_pixeles = corto_pix
    largo_pixeles = largo_pix
    hojabase_pixeles = hojabase_pix
    factor = conversion_factor

def rotateAndScale(img_binarizada, scaleFactor=0.5, theta=30):
    """Rotate and scale an image.
    
    Args:
        img_binarizada: The input image.
        scaleFactor: The scaling factor for the image.
        theta: The angle by which the image should be rotated.
    
    Returns:
        The rotated and scaled image.
    """
    (old_filas, old_columnas) = img_binarizada.shape[:2]
    Matriz_rotada = cv2.getRotationMatrix2D(center=(old_columnas / 2, old_filas / 2), angle=theta, scale=scaleFactor)
    new_columnas, new_filas = old_columnas * scaleFactor, old_filas * scaleFactor
    r = np.deg2rad(theta)
    new_columnas, new_filas = (abs(np.sin(r) * new_filas) + abs(np.cos(r) * new_columnas), 
                               abs(np.sin(r) * new_columnas) + abs(np.cos(r) * new_filas))
    (tx, ty) = ((new_columnas - old_columnas) / 2, (new_filas - old_filas) / 2)
    Matriz_rotada[0, 2] += tx
    Matriz_rotada[1, 2] += ty
    rotated_and_scaled_img = cv2.warpAffine(img_binarizada, Matriz_rotada, dsize=(int(new_columnas), int(new_filas)))
    return rotated_and_scaled_img

def segmentacion(original_image):
    """Segment an image to extract information about the cutting.
    
    Args:
        original_image: The input image.
    
    Returns:
        A tuple containing the average stem width, leaf area, rotated image, length in cm, classification, class, segmented image, and contour.
    """
    global corto_pixeles, largo_pixeles, hojabase_pixeles, factor

    ret, imagen_binarizada = cv2.threshold(original_image[:, :, 0], 20, 255, cv2.THRESH_BINARY_INV)
    contours, hierarchy = cv2.findContours(imagen_binarizada, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    contorno_esqueje = contours[0]
    imagen_binarizada[...] = 0
    cv2.drawContours(imagen_binarizada, [contorno_esqueje], 0, 255, cv2.FILLED)
    mascara = cv2.bitwise_and(original_image, original_image, mask=imagen_binarizada)
    centerContour, sizeContour, theta = cv2.fitEllipse(contorno_esqueje)
    esqueje_rotado = rotateAndScale(mascara, 1, theta)
    ret, imagen_binarizada_2 = cv2.threshold(esqueje_rotado[:, :, 1], 5, 255, cv2.THRESH_BINARY)
    contours2, hierarchy2 = cv2.findContours(imagen_binarizada_2, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    contours2 = sorted(contours2, key=cv2.contourArea, reverse=True)
    contorno_esqueje2 = contours2[0]
    imagen_binarizada_2[...] = 0
    cv2.drawContours(imagen_binarizada_2, [contorno_esqueje2], 0, 255, cv2.FILLED)
    x, y, w, h = cv2.boundingRect(contorno_esqueje2)
    dst_roi = esqueje_rotado[y:y + h, x:x + w]
    imagen_binarizada_3 = imagen_binarizada_2[y:y + h, x:x + w]
    cols, rows = dst_roi.shape[:2]
    if rows < cols:
        esqueje_rotado = rotateAndScale(dst_roi, 0.5, 90)
        imagen_binarizada_3 = rotateAndScale(imagen_binarizada_3, 0.5, 90)
    kernel = np.ones((5, 11), np.uint8)
    imagen_binarizada_3 = cv2.morphologyEx(imagen_binarizada_3, cv2.MORPH_OPEN, kernel)
    cols, rows = dst_roi.shape[:2]
    longitud_cm = cols * factor
    if cols < corto_pixeles and cols > 200:
        clasificacion = '1'
        clase = 'Corto'
    elif cols > largo_pixeles:
        clasificacion = '2'
        clase = 'Largo'
    elif cols < 200 or rows < 20:
        clasificacion = '0'
        clase = 'Nada'
    elif cols > corto_pixeles and cols < largo_pixeles:
        clasificacion = '4'
        clase = 'Ideal'
    else:
        clasificacion = '0'
        clase = 'Vacio'
    if clase != 'Corto':
        a = 0
        b = 0
        d = 0
        row, col = imagen_binarizada_3.shape
        for c in range(col):
            a = np.append(a, (imagen_binarizada_3[:, c] > 100).sum())
        promedio = np.average(a[np.uint(a.size * 0.01):np.uint(a.size * 0.5)])
        if promedio < 100:
            b = a
        else:
            b = np.flipud(a)
        if np.uint(b.size) > 200:
            b = savitzky_golay(b, 11, 1)
            b = savitzky_golay(b, 11, 1)
            d = np.diff(b)
            d = savitzky_golay(d, 11, 1)
            promedio = np.average(b[np.uint(hojabase_pixeles * 0.4):np.uint(hojabase_pixeles * 0.5)])
            valor_hojabase_pixeles = b[hojabase_pixeles]
            if np.abs(valor_hojabase_pixeles - promedio) > np.uint(promedio * 0.22):
                clasificacion = '3'
                clase = 'Hoja en base'
    tallo_promedio, area_foliar = encontrar_medidas(esqueje_rotado)
    ret_esqueje_rotado = esqueje_rotado
    b, g, r = cv2.split(esqueje_rotado)
    esqueje_rotado = cv2.merge([r, g, b])
    return tallo_promedio, area_foliar, ret_esqueje_rotado, longitud_cm, clasificacion, clase, dst_roi.copy(), contorno_esqueje2

def encontrar_medidas(imagen):
    """Find the average stem width and leaf area of a cutting.
    
    Args:
        imagen: The input image.
    
    Returns:
        A tuple containing the average stem width and leaf area.
    """
    gray = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape
    stem_area = gray[:, :w // 3]
    leaf_area = gray[:, w // 3:]
    stem_nonzero_counts = np.count_nonzero(stem_area, axis=0)
    average_stem_width = np.mean(stem_nonzero_counts)
    upper_leaf_area = leaf_area[:h // 2, :]
    lower_leaf_area = leaf_area[h // 2:, :]
    upper_nonzero_counts = np.count_nonzero(upper_leaf_area)
    lower_nonzero_counts = np.count_nonzero(lower_leaf_area)
    larger_leaf_area = max(upper_nonzero_counts, lower_nonzero_counts)
    scale_factor = (10.5 / 960) ** 2
    leaf_area_scaled = larger_leaf_area * scale_factor
    return average_stem_width * scale_factor, leaf_area_scaled

def savitzky_golay(y, window_size, order, deriv=0, rate=1):
    """Smooth (and optionally differentiate) data with a Savitzky-Golay filter.
    
    Args:
        y: The data to be smoothed.
        window_size: The size of the window.
        order: The order of the polynomial.
        deriv: The order of the derivative.
        rate: The rate of the derivative.
    
    Returns:
        The smoothed data.
    """
    try:
        window_size = abs(int(window_size))
        order = abs(int(order))
    except ValueError:
        raise ValueError("window_size and order have to be of type int")
    if window_size % 2 != 1 or window_size < 1:
        raise TypeError("window_size size must be a positive odd number")
    if window_size < order + 2:
        raise TypeError("window_size is too small for the polynomials order")
    order_range = range(order + 1)
    half_window = (window_size - 1) // 2
    b = np.mat([[k ** i for i in order_range] for k in range(-half_window, half_window + 1)])
    m = np.linalg.pinv(b).A[deriv] * rate ** deriv * factorial(deriv)
    firstvals = y[0] - np.abs(y[1:half_window + 1][::-1] - y[0])
    lastvals = y[-1] + np.abs(y[-half_window - 1:-1][::-1] - y[-1])
    y = np.concatenate((firstvals, y, lastvals))
    return np.convolve(m[::-1], y, mode='valid')