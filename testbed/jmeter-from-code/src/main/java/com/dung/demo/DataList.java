package com.dung.demo;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;

/**
 * Created by dungvt on 26/05/2017.
 */
public class DataList {
    private double[] data;
    private double v;

    public DataList(String file, int begin, int end) {
        readFile(file);
        processData(begin, end);
    }

    public void readFile(String filePath) {
        try {
            File file = new File(filePath);
            FileReader fileReader = new FileReader(file);
            BufferedReader bufferedReader = new BufferedReader(fileReader);
            ArrayList<Double> tdata = new ArrayList<Double>();
            String line;
            double prevv = 0;
            while ((line = bufferedReader.readLine()) != null) {
                double v = Double.parseDouble(line);
                if (v <= 0) v = prevv;
                prevv = v;

                tdata.add(v);
            }
            fileReader.close();

            data = new double[tdata.size()];
            for (int i = 0; i < tdata.size(); i++) {
                data[i] = tdata.get(i);
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public void processData(int begin, int end) {
        double[] tdata = new double[end - begin];

        int idx = 0;
        for (int i = begin; i < end; i++) {
            double val = Math.log10(Math.log10(data[i]));
            tdata[idx++] = val;
        }
        data = tdata;

        // normalize
        double max = Double.MIN_VALUE;
        double min = Double.MAX_VALUE;
        for (int i = 0; i < data.length; i++) {
            if (max < data[i]) max = data[i];
            if (min > data[i]) min = data[i];
        }
        for (int i = 0; i < data.length; i++) {
            data[i] = (data[i] - min) / (max - min);
        }
    }

    public double[] getData() {
        return data;
    }

    public void printData() {
        for (int i = 0; i < data.length; i++) {
            System.out.println(data[i]);
        }
    }


    public static void main(String[] args) {
        DataList dataObject = new DataList("/home/dungvt/SpaceYZ/projects/graduation/10min_workload.csv", 48 * 142, 55 * 142);
        dataObject.printData();
    }
}
