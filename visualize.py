import json
import xlsxwriter

def get_spec_station(stations, iid):
    return next((s for s in stations if s["id"] == iid))

def estation_weekday(filename, stations):
    """ Usado para salidas y llegadas """
    workbook = xlsxwriter.Workbook('{}.xlsx'.format(filename[:-5]))
    data, row = json.load(open(filename)), 1
    worksheet = workbook.add_worksheet()

    # Escritura de headers
    worksheet.write(0, 0, "Nombre estación")
    worksheet.write(0, 1, "Lunes")
    worksheet.write(0, 2, "Martes")
    worksheet.write(0, 3, "Miércoles")
    worksheet.write(0, 4, "Jueves")
    worksheet.write(0, 5, "Viernes")
    worksheet.write(0, 6, "Sábado")
    worksheet.write(0, 7, "Domingo")
    worksheet.write(0, 8, "Total")
    worksheet.write(0, 9, "Id estación")

    for k, v in data.items():
        station = get_spec_station(stations, int(k))
        worksheet.write(row, 0, station['name'])
        worksheet.write(row, 1, v['Lunes'])
        worksheet.write(row, 2, v['Martes'])
        worksheet.write(row, 3, v['Miercoles'])
        worksheet.write(row, 4, v['Jueves'])
        worksheet.write(row, 5, v['Viernes'])
        worksheet.write(row, 6, v['Sabado'])
        worksheet.write(row, 7, v['Domingo'])
        worksheet.write(row, 8, sum(v.values()))
        worksheet.write(row, 9, int(k))
        row += 1

    # Agregar filtros y guardar
    worksheet.autofilter('A1:J{}'.format(row))
    workbook.close()

def viajes_weekday(filename):
    """ Usado para trips_weekday_%Y """
    workbook = xlsxwriter.Workbook('{}.xlsx'.format(filename[:-5]))
    data, row = json.load(open(filename)), 1
    worksheet = workbook.add_worksheet()

    # Escritura de headers
    worksheet.write(0, 0, "Día")
    worksheet.write(0, 1, "Viajes")

    for k in ['Lunes', 'Martes', 'Miercoles', 'Jueves', 'Viernes', 'Sabado', 'Domingo']:
        worksheet.write(row, 0, k)
        worksheet.write(row, 1, data[k])
        row += 1

    # Agregar filtros y guardar
    worksheet.autofilter('A1:B{}'.format(row))
    workbook.close()

def distribucion_weekday(filename):
    """ Usado para trip_distribution_%Y """
    workbook = xlsxwriter.Workbook('{}.xlsx'.format(filename[:-5]))
    data, row = json.load(open(filename)), 1
    worksheet = workbook.add_worksheet()

    # Escritura de headers
    worksheet.write(0, 0, "Día")
    worksheet.write(0, 1, "Viajes")

    for k, v in data.items():
        worksheet.write(row, 0, k)
        worksheet.write(row, 1, v)
        row += 1

    # Agregar filtros y guardar
    worksheet.autofilter('A1:B{}'.format(row))
    workbook.close()

def durante_dia(filename):
    """ Usado para trips_during_day_%D """
    workbook = xlsxwriter.Workbook('{}.xlsx'.format(filename[:-5]))
    data, row = json.load(open(filename)), 1
    worksheet = workbook.add_worksheet()

    # Escritura de headers
    worksheet.write(0, 0, "Hora")
    worksheet.write(0, 1, "Viajes")

    for k, v in data.items():
        worksheet.write(row, 0, k)
        worksheet.write(row, 1, v)
        row += 1

    # Agregar filtros y guardar
    worksheet.autofilter('A1:B{}'.format(row))
    workbook.close()

def viajes_totales(llegadas, salidas, stations):
    workbook = xlsxwriter.Workbook('data/llegadas_totales.xlsx')
    worksheet = workbook.add_worksheet()
    worksheet.write(0, 0, 'Estacion')  # Header
    col = 1
    for l, s in zip(llegadas, salidas):
        lleg, sal = json.load(open(l)), json.load(open(s))
        worksheet.write(0, col, l[-9:-5])  # Header
        row = 1
        for station in stations:
            total = sum(lleg[str(station)].values()) + sum(sal[str(station)].values())
            worksheet.write(row, col, total)
            worksheet.write(row, 0, station)
            row += 1
        col += 1

    # Agregar filtros y guardar
    worksheet.autofilter('A1:D{}'.format(row))
    workbook.close()

def heatmap(llegadas, salidas, stations):
    # Se necesita el objeto completo de stations
    lleg = [json.load(open(l)) for l in llegadas]
    sal = [json.load(open(s)) for s in salidas]
    codelines = []
    for st in stations:
        total = sum([sum(l[str(st['id'])].values()) for l in lleg] + [sum(s[str(st['id'])].values()) for s in sal])
        repeticiones = int(total/10000)
        for r in range(repeticiones):
            codelines.append('new google.maps.LatLng({}, {})'.format(st['location']['lat'], st['location']['lon']))
    with open('data/heatmap.json', 'w') as f:
        f.write(json.dumps({'data': codelines}, sort_keys=True, indent=4))

def visualize_analyze_trips_by_moments_day_station(filenames, station, extra_info=''):
    workbook = xlsxwriter.Workbook('data/estacion_{}{}.xlsx'.format(station, extra_info))
    worksheet1 = workbook.add_worksheet('Llegadas')
    worksheet2 = workbook.add_worksheet('Salidas')
    jsons = []
    # Escribir headers
    worksheet1.write(0, 0, 'Hora')
    worksheet2.write(0, 0, 'Hora')
    for col, filename in enumerate(filenames):
        worksheet1.write(0, col + 1, filename[11:21])
        worksheet2.write(0, col + 1, filename[11:21])
        jsons.append(json.load(open(filename)))
    # Escribir datos
    for row, key in enumerate(jsons[0]):
        worksheet1.write(row + 1, 0, key)
        worksheet2.write(row + 1, 0, key)
        for col, day in enumerate(jsons):
            worksheet1.write(row + 1, col + 1, day[key]['llegadas'])
            worksheet2.write(row + 1, col + 1, day[key]['salidas'])
    # Guardar el .xlsx
    workbook.close()
