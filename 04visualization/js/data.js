// 自动生成的模型数据
// 生成时间: 2025-12-27 11:05:06
// 修复时间: 2025-12-29 (删除重复数据，修复语法错误)

const MODEL_DATA = {
  "PyTorch_ResNet": {
    "overall": {
        "accuracy": 0.9765,
        "precision": 0.9674,
        "recall": 0.986,
        "f1": 0.9766,
        "specificity": 0.9671,
        "confusion_matrix": {
            "TP": 772,
            "TN": 764,
            "FP": 26,
            "FN": 11
        },
        "avg_confidence": 0.9708,
        "total": 1573,
        "confidence_distribution": [
            19,
            31,
            25,
            61,
            69,
            1368
        ]
    },
    "cataract": {
        "precision": 0.9674,
        "recall": 0.986,
        "accuracy": 0.986,
        "f1": 0.9766,
        "count": 783,
        "correct": 772,
        "avg_confidence": 0.966,
    },
    "normal": {
        "precision": 0.9858,
        "recall": 0.9671,
        "accuracy": 0.9671,
        "f1": 0.9764,
        "count": 790,
        "correct": 764,
        "avg_confidence": 0.9756,
    }
},

  "C组": {
    "overall": {
      "accuracy": 0.9763,
      "precision": 0.9592,
      "recall": 0.7833,
      "f1": 0.8624,
      "specificity": 0.9965,
      "confusion_matrix": {
        "TP": 47,
        "TN": 572,
        "FP": 2,
        "FN": 13
      },
      "avg_confidence": 0.9844,
      "total": 634,
      "confidence_distribution": [
        0,
        6,
        7,
        4,
        15,
        602
      ]
    },
    "cataract": {
      "precision": 0.9592,
      "recall": 0.7833,
      "count": 60,
      "correct": 47,
      "avg_confidence": 0.9141,
      "accuracy": 0.7833,
      "f1": 0.8624,
    },
    "normal": {
      "precision": 0.9778,
      "recall": 0.9965,
      "count": 574,
      "correct": 572,
      "avg_confidence": 0.9917,
      "accuracy": 0.9965,
      "f1": 0.9871,
    }
  },
  "finalmodel": {
    "overall": {
      "accuracy": 0.9854,
      "precision": 0.9859,
      "recall": 0.9847,
      "f1": 0.9853,
      "specificity": 0.9861,
      "confusion_matrix": {
        "TP": 771,
        "TN": 779,
        "FP": 11,
        "FN": 12
      },
      "avg_confidence": 0.9943,
      "total": 1573,
      "confidence_distribution": [
        0,
        2,
        6,
        12,
        11,
        1542
      ]
    },
    "cataract": {
      "precision": 0.9859,
      "recall": 0.9847,
      "accuracy": 0.9847,
      "f1": 0.9853,
      "count": 783,
      "correct": 771,
      "avg_confidence": 0.982,
    },
    "normal": {
      "precision": 0.9848,
      "recall": 0.9861,
      "accuracy": 0.9861,
      "f1": 0.9854,
      "count": 790,
      "correct": 779,
      "avg_confidence": 0.998,
    }
  },
  "modelA1测试报告": {
    "overall": {
      "accuracy": 0.7942,
      "precision": 0.9793,
      "recall": 0.5772,
      "f1": 0.7263,
      "specificity": 0.9891,
      "confusion_matrix": {
        "TP": 142,
        "TN": 271,
        "FP": 3,
        "FN": 104
      },
      "avg_confidence": 0.98,
      "total": 520,
      "confidence_distribution": [
        0,
        6,
        6,
        8,
        14,
        486
      ]
    },
    "cataract": {
      "precision": 0.9793,
      "recall": 0.5772,
      "count": 246,
      "correct": 142,
      "avg_confidence": 0.962,
      "accuracy": 0.5772,
      "f1": 0.7263,
    },
    "normal": {
      "precision": 0.7227,
      "recall": 0.9891,
      "count": 274,
      "correct": 271,
      "avg_confidence": 0.9963,
      "accuracy": 0.9891,
      "f1": 0.8352,
    }
  },
  "modelA2测试报告": {
    "overall": {
      "accuracy": 0.8654,
      "precision": 0.9583,
      "recall": 0.748,
      "f1": 0.8402,
      "specificity": 0.9708,
      "confusion_matrix": {
        "TP": 184,
        "TN": 266,
        "FP": 8,
        "FN": 62
      },
      "avg_confidence": 0.9615,
      "total": 520,
      "confidence_distribution": [
        0,
        9,
        14,
        14,
        26,
        457
      ]
    },
    "cataract": {
      "precision": 0.9583,
      "recall": 0.748,
      "count": 246,
      "correct": 184,
      "avg_confidence": 0.9378,
      "accuracy": 0.748,
      "f1": 0.8402,
    },
    "normal": {
      "precision": 0.811,
      "recall": 0.9708,
      "count": 274,
      "correct": 266,
      "avg_confidence": 0.9828,
      "accuracy": 0.9708,
      "f1": 0.8837,
    }
  },
  "modelA3测试报告": {
    "overall": {
      "accuracy": 0.8231,
      "precision": 0.9812,
      "recall": 0.6382,
      "f1": 0.7734,
      "specificity": 0.9891,
      "confusion_matrix": {
        "TP": 157,
        "TN": 271,
        "FP": 3,
        "FN": 89
      },
      "avg_confidence": 0.9588,
      "total": 520,
      "confidence_distribution": [
        0,
        14,
        14,
        19,
        23,
        450
      ]
    },
    "cataract": {
      "precision": 0.9812,
      "recall": 0.6382,
      "count": 246,
      "correct": 157,
      "avg_confidence": 0.924,
      "accuracy": 0.6382,
      "f1": 0.7734,
    },
    "normal": {
      "precision": 0.7528,
      "recall": 0.9891,
      "count": 274,
      "correct": 271,
      "avg_confidence": 0.99,
      "accuracy": 0.9891,
      "f1": 0.8549,
    }
  },
  "modelB1测试报告": {
    "overall": {
      "accuracy": 0.9549,
      "precision": 0.9352,
      "recall": 0.9758,
      "f1": 0.9551,
      "specificity": 0.9346,
      "confusion_matrix": {
        "TP": 202,
        "TN": 200,
        "FP": 14,
        "FN": 5
      },
      "avg_confidence": 0.9919,
      "total": 421,
      "confidence_distribution": [
        0,
        2,
        2,
        2,
        4,
        411
      ]
    },
    "cataract": {
      "precision": 0.9352,
      "recall": 0.9758,
      "count": 207,
      "correct": 202,
      "avg_confidence": 0.9954,
      "accuracy": 0.9758,
      "f1": 0.9551,
    },
    "normal": {
      "precision": 0.9756,
      "recall": 0.9346,
      "count": 214,
      "correct": 200,
      "avg_confidence": 0.9886,
      "accuracy": 0.9346,
      "f1": 0.9547,
    }
  },
  "modelB2测试报告": {
    "overall": {
      "accuracy": 0.9549,
      "precision": 0.9608,
      "recall": 0.9469,
      "f1": 0.9538,
      "specificity": 0.9626,
      "confusion_matrix": {
        "TP": 196,
        "TN": 206,
        "FP": 8,
        "FN": 11
      },
      "avg_confidence": 0.9696,
      "total": 421,
      "confidence_distribution": [
        0,
        10,
        7,
        5,
        11,
        388
      ]
    },
    "cataract": {
      "precision": 0.9608,
      "recall": 0.9469,
      "count": 207,
      "correct": 196,
      "avg_confidence": 0.9619,
      "accuracy": 0.9469,
      "f1": 0.9538,
    },
    "normal": {
      "precision": 0.9493,
      "recall": 0.9626,
      "count": 214,
      "correct": 206,
      "avg_confidence": 0.9771,
      "accuracy": 0.9626,
      "f1": 0.9559,
    }
  },
  "modelB3测试报告": {
    "overall": {
      "accuracy": 0.9644,
      "precision": 0.9948,
      "recall": 0.9324,
      "f1": 0.9626,
      "specificity": 0.9953,
      "confusion_matrix": {
        "TP": 193,
        "TN": 213,
        "FP": 1,
        "FN": 14
      },
      "avg_confidence": 0.981,
      "total": 421,
      "confidence_distribution": [
        0,
        10,
        2,
        2,
        7,
        400
      ]
    },
    "cataract": {
      "precision": 0.9948,
      "recall": 0.9324,
      "count": 207,
      "correct": 193,
      "avg_confidence": 0.9744,
      "accuracy": 0.9324,
      "f1": 0.9626,
    },
    "normal": {
      "precision": 0.9383,
      "recall": 0.9953,
      "count": 214,
      "correct": 213,
      "avg_confidence": 0.9873,
      "accuracy": 0.9953,
      "f1": 0.966,
    }
  }
};


// 模型列表
const MODEL_NAMES = ["PyTorch_ResNet", "C组", "finalmodel", "modelA1测试报告", "modelA2测试报告", "modelA3测试报告", "modelB1测试报告", "modelB2测试报告", "modelB3测试报告"];

// 导出数据
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { MODEL_DATA, MODEL_NAMES };
}
