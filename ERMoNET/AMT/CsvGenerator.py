import csv

class CsvGenerator:

    def downloadCsv(self, result, tasktype, names):
        with open('csvfile.csv', 'w') as myfile:
                wr = csv.writer(myfile, quoting=csv.QUOTE_NONE)
                if tasktype == "binary":
                    wr.writerow(["Location","Result","Annotator"])
                else:
                    wr.writerow(["Image_set", "Result"])
                for i in range(0, len(result)):
                    wr.writerow(result[i])

        return True

    def downloadCategoricalCsv(self, result, tasktype, total, selected):
        global result_list
        with open('csvfile.csv', 'w') as myfile:

            if tasktype == "categorical":
                wr = csv.writer(myfile, quoting=csv.QUOTE_NONE)
                header = ["Location", "Result", "Annotator"]

                category_list = []
                for i in range(0, len(total)):
                    category_list.append(total[i][0].split())

                selected_list = []
                for i in range(0, len(selected)):
                    selected_list.append(selected[i][0].split())

                for j in range(0, len(category_list)):
                    for k in range(0, len(category_list[j])):
                        header.append(category_list[j][k])

                wr.writerow(header)

                for i in range (0,len(result)):
                    for j in range (3, len(header)):
                        result_list = list(result[i])
                        result_list.insert(j, "false")
                        result[i] = tuple(result_list)

            try:
                index = -1
                for a in range(0, len(selected_list)):
                    index=index+1
                    for b in range(0, len(selected_list[a])):
                        for j in range(3, len(header)):
                            if header[j] == selected_list[a][b]:
                                result_list = list(result[index])
                                result_list[j] = "true"
                                result[index] = tuple(result_list)
            except Exception as e:
                print (e)

            for i in range(0, len(result)):
                wr.writerow(result[i])

        return True

    def downloadCategoricalSingleCsv(self, result, tasktype, total, selected, single, singleheader):
        global result_list, single_header_list
        with open('csvfile.csv', 'w') as myfile:

            if tasktype == "categorical":
                wr = csv.writer(myfile, quoting=csv.QUOTE_NONE)
                header = ["Location", "Result", "Annotator"]

                category_list = []
                for i in range(0, len(total)):
                    category_list.append(total[i][0].split())

                selected_list = []
                for i in range(0, len(selected)):
                    selected_list.append(selected[i][0].split())

                for j in range(0, len(category_list)):
                    for k in range(0, len(category_list[j])):
                        header.append(category_list[j][k])

                single_header_list = []
                for i in range(0, len(singleheader)):
                    if singleheader[i][0] != None:
                        single_header_list.append(singleheader[i][0].split())



                for i in range (0,len(result)):
                    for j in range (3, len(header)):
                        result_list = list(result[i])
                        result_list.insert(j, "false")
                        result[i] = tuple(result_list)

            try:
                index = -1
                for a in range(0, len(selected_list)):
                    index=index+1
                    for b in range(0, len(selected_list[a])):
                        for j in range(3, len(header)):
                            if header[j] == selected_list[a][b]:
                                result_list = list(result[index])
                                result_list[j] = "true"
                                result[index] = tuple(result_list)
            except Exception as e:
                print (e)


            single_selected_list = []
            for i in range(0, len(single)):
                single_selected_list.append(single[i][0].split())


            for j in range(0, len(single_header_list)):
                for k in range(0, len(single_header_list[j])):
                        header.append(single_header_list[j][k])


            try:
                for i in range(0, len(single_selected_list)):
                    for j in range(0,len(single_selected_list[i])):
                        result_list = list(result[i])
                        result_list.append(single_selected_list[i][j])
                        result[i] = tuple(result_list)

            except Exception as e:
                print (e)

            wr.writerow(header)
            for i in range(0, len(result)):
                wr.writerow(result[i])

        return True
