import math
import os

import vtk


def load_vtp(filepath: str):
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"file {filepath} not found")
    reader = vtk.vtkXMLPolyDataReader()
    reader.SetFileName(filepath)
    reader.Update()
    polydata = reader.GetOutput()
    print(f"nbr of points: {polydata.GetPoints().GetNumberOfPoints()}")
    return polydata


def save_stl(filepath, data):
    writer = vtk.vtkSTLWriter()
    writer.SetFileName(filepath)
    writer.SetFileTypeToBinary()
    writer.SetInputData(data)
    writer.Write()


def get_configuration(polydata, smoothing_length, cell_size):
    offset = 4 * max(smoothing_length, cell_size)
    bbox = [0] * 6
    polydata.GetBounds(bbox)
    dimensions = [bbox[1] - bbox[0], bbox[3] - bbox[2], bbox[5] - bbox[4]]
    nbr_cells = [None] * 3
    for i, dim in enumerate(dimensions):
        nbr_cells[i] = int(math.ceil((dim + 2 * offset) / cell_size))
    grid_minimum = [bbox[0] - offset, bbox[2] - offset, bbox[4] - offset]
    return nbr_cells, grid_minimum


def contour(grid, alpha):
    contour = vtk.vtkContourFilter()
    contour.SetInputData(grid)
    contour.ComputeNormalsOn()
    contour.SetValue(0, alpha)
    contour.Update()
    return contour.GetOutput()


def get_attribute_names(polydata):
    attr_names = []
    point_data = polydata.GetPointData()
    nr_of_attributes = point_data.GetNumberOfArrays()
    for i in range(nr_of_attributes):
        attr_names.append(point_data.GetArrayName(i))
    return attr_names


def sph(h, input, source_poly):
    sphKernel = vtk.vtkWendlandQuinticKernel()
    sphKernel.SetSpatialStep(h)
    interpolator = vtk.vtkSPHInterpolator()
    interpolator.SetInputData(input)
    interpolator.SetSourceData(source_poly)
    interpolator.SetDensityArrayName("density")
    interpolator.SetMassArrayName("mass")

    for attr in get_attribute_names(source_poly):
        interpolator.AddExcludedArray(attr)

    interpolator.ClearDerivativeArrays()
    interpolator.ComputeShepardSumOn()
    interpolator.SetKernel(sphKernel)
    interpolator.Update()
    retval = interpolator.GetOutput()
    retval.GetPointData().SetActiveScalars("Shepard Summation")
    return retval


def vtk_image_data(minimum: list, cell: float, dimensions: list[int]):
    grid = vtk.vtkImageData()
    grid.SetOrigin(minimum)
    grid.SetSpacing(cell, cell, cell)
    grid.SetDimensions(dimensions)
    print(f"nbr of cells in grid: {grid.GetNumberOfCells()}")
    return grid


def surface_pipeline(input_file_path, output_file_path, cell_size, alpha=0.5):
    polydata = load_vtp(input_file_path)
    nbr_cells, grid_minimum = get_configuration(polydata, cell_size, cell_size)
    grid = vtk_image_data(grid_minimum, cell_size, nbr_cells)
    retval_interpolate = sph(cell_size, grid, polydata)
    retval = contour(retval_interpolate, alpha)
    save_stl(output_file_path, retval)
