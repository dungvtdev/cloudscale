package com.dung.demo;

import kg.apc.jmeter.threads.UltimateThreadGroupGui;
import org.apache.jmeter.gui.util.PowerTableModel;

import java.util.ArrayList;

/**
 * Created by dungvt on 26/05/2017.
 */
public class ExperimentData {
    int[][] data = new int[][]{
            {27, 0, 237, 10, 400},
            {10, 310, 100, 20, 700},
            {5, 650, 30, 600, 300},
            {24, 720, 220, 60, 300},
            {10, 1100, 80, 10, 200},
            {8, 1400, 30, 600, 100},
            {20, 1450, 200, 20, 100},
            {18, 1600, 200, 20, 500},
            {15, 2400, 200, 60, 250},
            {8, 2750, 30, 60, 520},
            {5, 3000, 30, 60, 200},
            {12, 3300, 200, 400, 50,},
            {12, 3920, 30, 300, 150},
            {25, 4100, 400, 30, 300},
            {15, 4650, 300, 60, 150},
            {32, 5000, 300, 60, 150},
            {25, 5400, 150, 60, 200},
            {10, 5700, 100, 200, 50}
    };

    public int getDataTimeLength() {
        int[] last = data[data.length-1];
        return last[1] + last[2] + last[3] + last[4];
    }

    public int getMaxValue() {
        return 34;
    }

    public PowerTableModel getTable(float normalize_begin, float normalize_end, int max_length, int max_val) {
        if(max_length==0)
            max_length = getDataTimeLength();
        if(max_val==0)
            max_val = getMaxValue();

        int begin = (int) (getDataTimeLength() * normalize_begin);
        int end = (int) (getDataTimeLength() * normalize_end);
        ArrayList<int[]> temp = null;
        for (int i = 0; i < data.length; i++) {
            int v = data[i][1] + data[i][2];
            if (v >= begin && v <= end) {
                if (temp == null) {
                    temp = new ArrayList<int[]>();
                }
                temp.add(data[i]);
                data[i][1] -= begin;
            } else if (temp != null) {
                break;
            }
        }

        if (max_val != getMaxValue()) {
            for (int[] d : temp) {
                d[0] = (int) (d[0] * max_val * 1.0f / getMaxValue());
            }
        }

        if (max_length != getDataTimeLength()) {
            for (int[] d : temp) {
                for (int i = 1; i < 5; i++) {
                    d[i] = (int) (d[i] * max_length * 1.0f / getDataTimeLength());
                }
            }
        }

        PowerTableModel dataModel = new PowerTableModel(UltimateThreadGroupGui.columnIdentifiers, UltimateThreadGroupGui.columnClasses);
        for (int[] d : temp) {
            dataModel.addRow(new Integer[]{
                    d[0], d[1], d[2], d[3], d[4]
            });
        }
        return dataModel;
    }

    public static void main(String[] args) {
        ExperimentData dataObject = new ExperimentData();
        PowerTableModel model = dataObject.getTable(0,1,24*3600*2, 60);
        System.out.println(model);
    }
}
