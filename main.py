import glob

import utils as ut

if __name__ == '__main__':

    data_dict = {}

    # загружаем файлы
    f_s = ut.get_initial_info()

    # проверяем изменения в фидах
    if ut.check_counter(f_s):

        # обрабатываем загруженные файлы
        for filename in glob.glob("xml_files/*.xml"):
            ut.xml_files_proccessing(filename, data=data_dict)

        # создаем выходной файл
        ut.generate_output_file(data_dict)

    else:
        print('Модификация файла не требуется')

    # Сохраняем хэш содержимого для дальнейшей проверки
    ut.save_hash(f_s)
