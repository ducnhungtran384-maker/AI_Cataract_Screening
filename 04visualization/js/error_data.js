const ERROR_CASES = [
  {
    "filename": "cataract_1155.jpg",
    "true_label": "Cataract",
    "pred_label": "Normal",
    "confidence": 0.64181167,
    "image_path": "error_images/cataract_1155.jpg"
  },
  {
    "filename": "cataract_12.jpg",
    "true_label": "Cataract",
    "pred_label": "Normal",
    "confidence": 0.96772844,
    "image_path": "error_images/cataract_12.jpg"
  },
  {
    "filename": "cataract_1319.jpg",
    "true_label": "Cataract",
    "pred_label": "Normal",
    "confidence": 0.62607634,
    "image_path": "error_images/cataract_1319.jpg"
  },
  {
    "filename": "cataract_2197.jpg",
    "true_label": "Cataract",
    "pred_label": "Normal",
    "confidence": 0.9060927,
    "image_path": "error_images/cataract_2197.jpg"
  },
  {
    "filename": "cataract_2356.jpg",
    "true_label": "Cataract",
    "pred_label": "Normal",
    "confidence": 0.83677047,
    "image_path": "error_images/cataract_2356.jpg"
  },
  {
    "filename": "cataract_2408.jpg",
    "true_label": "Cataract",
    "pred_label": "Normal",
    "confidence": 0.95724493,
    "image_path": "error_images/cataract_2408.jpg"
  },
  {
    "filename": "cataract_3278.jpg",
    "true_label": "Cataract",
    "pred_label": "Normal",
    "confidence": 0.50114828,
    "image_path": "error_images/cataract_3278.jpg"
  },
  {
    "filename": "cataract_3392.jpg",
    "true_label": "Cataract",
    "pred_label": "Normal",
    "confidence": 0.57406503,
    "image_path": "error_images/cataract_3392.jpg"
  },
  {
    "filename": "cataract_3459.jpg",
    "true_label": "Cataract",
    "pred_label": "Normal",
    "confidence": 0.71817678,
    "image_path": "error_images/cataract_3459.jpg"
  },
  {
    "filename": "cataract_3660.jpg",
    "true_label": "Cataract",
    "pred_label": "Normal",
    "confidence": 0.53991944,
    "image_path": "error_images/cataract_3660.jpg"
  },
  {
    "filename": "cataract_3874.jpg",
    "true_label": "Cataract",
    "pred_label": "Normal",
    "confidence": 0.76390052,
    "image_path": "error_images/cataract_3874.jpg"
  },
  {
    "filename": "normal_1160.jpg",
    "true_label": "Normal",
    "pred_label": "Cataract",
    "confidence": 0.54214883,
    "image_path": "error_images/normal_1160.jpg"
  },
  {
    "filename": "normal_1171.jpg",
    "true_label": "Normal",
    "pred_label": "Cataract",
    "confidence": 0.60895437,
    "image_path": "error_images/normal_1171.jpg"
  },
  {
    "filename": "normal_1221.jpg",
    "true_label": "Normal",
    "pred_label": "Cataract",
    "confidence": 0.95825988,
    "image_path": "error_images/normal_1221.jpg"
  },
  {
    "filename": "normal_1242.jpg",
    "true_label": "Normal",
    "pred_label": "Cataract",
    "confidence": 0.94638777,
    "image_path": "error_images/normal_1242.jpg"
  },
  {
    "filename": "normal_1292.jpg",
    "true_label": "Normal",
    "pred_label": "Cataract",
    "confidence": 0.73005611,
    "image_path": "error_images/normal_1292.jpg"
  },
  {
    "filename": "normal_1313.jpg",
    "true_label": "Normal",
    "pred_label": "Cataract",
    "confidence": 0.95382971,
    "image_path": "error_images/normal_1313.jpg"
  },
  {
    "filename": "normal_1319.jpg",
    "true_label": "Normal",
    "pred_label": "Cataract",
    "confidence": 0.66516238,
    "image_path": "error_images/normal_1319.jpg"
  },
  {
    "filename": "normal_1391.jpg",
    "true_label": "Normal",
    "pred_label": "Cataract",
    "confidence": 0.85996342,
    "image_path": "error_images/normal_1391.jpg"
  },
  {
    "filename": "normal_1459.jpg",
    "true_label": "Normal",
    "pred_label": "Cataract",
    "confidence": 0.93813545,
    "image_path": "error_images/normal_1459.jpg"
  },
  {
    "filename": "normal_1580.jpg",
    "true_label": "Normal",
    "pred_label": "Cataract",
    "confidence": 0.9925794,
    "image_path": "error_images/normal_1580.jpg"
  },
  {
    "filename": "normal_1684.jpg",
    "true_label": "Normal",
    "pred_label": "Cataract",
    "confidence": 0.83716995,
    "image_path": "error_images/normal_1684.jpg"
  },
  {
    "filename": "normal_1976.jpg",
    "true_label": "Normal",
    "pred_label": "Cataract",
    "confidence": 0.60728198,
    "image_path": "error_images/normal_1976.jpg"
  },
  {
    "filename": "normal_2161.jpg",
    "true_label": "Normal",
    "pred_label": "Cataract",
    "confidence": 0.87210834,
    "image_path": "error_images/normal_2161.jpg"
  },
  {
    "filename": "normal_2472.jpg",
    "true_label": "Normal",
    "pred_label": "Cataract",
    "confidence": 0.66735822,
    "image_path": "error_images/normal_2472.jpg"
  },
  {
    "filename": "normal_2516.jpg",
    "true_label": "Normal",
    "pred_label": "Cataract",
    "confidence": 0.89386564,
    "image_path": "error_images/normal_2516.jpg"
  },
  {
    "filename": "normal_2654.jpg",
    "true_label": "Normal",
    "pred_label": "Cataract",
    "confidence": 0.93291807,
    "image_path": "error_images/normal_2654.jpg"
  },
  {
    "filename": "normal_2861.jpg",
    "true_label": "Normal",
    "pred_label": "Cataract",
    "confidence": 0.77010769,
    "image_path": "error_images/normal_2861.jpg"
  },
  {
    "filename": "normal_2984.jpg",
    "true_label": "Normal",
    "pred_label": "Cataract",
    "confidence": 0.59026915,
    "image_path": "error_images/normal_2984.jpg"
  },
  {
    "filename": "normal_2986.jpg",
    "true_label": "Normal",
    "pred_label": "Cataract",
    "confidence": 0.6942032,
    "image_path": "error_images/normal_2986.jpg"
  },
  {
    "filename": "normal_3000.jpg",
    "true_label": "Normal",
    "pred_label": "Cataract",
    "confidence": 0.63442343,
    "image_path": "error_images/normal_3000.jpg"
  },
  {
    "filename": "normal_3009.jpg",
    "true_label": "Normal",
    "pred_label": "Cataract",
    "confidence": 0.90500009,
    "image_path": "error_images/normal_3009.jpg"
  },
  {
    "filename": "normal_3136.jpg",
    "true_label": "Normal",
    "pred_label": "Cataract",
    "confidence": 0.89986074,
    "image_path": "error_images/normal_3136.jpg"
  },
  {
    "filename": "normal_3192.jpg",
    "true_label": "Normal",
    "pred_label": "Cataract",
    "confidence": 0.804537,
    "image_path": "error_images/normal_3192.jpg"
  },
  {
    "filename": "normal_3919.jpg",
    "true_label": "Normal",
    "pred_label": "Cataract",
    "confidence": 0.88975537,
    "image_path": "error_images/normal_3919.jpg"
  },
  {
    "filename": "normal_682.jpg",
    "true_label": "Normal",
    "pred_label": "Cataract",
    "confidence": 0.66708505,
    "image_path": "error_images/normal_682.jpg"
  },
  {
    "filename": "normal_746.jpg",
    "true_label": "Normal",
    "pred_label": "Cataract",
    "confidence": 0.8700943,
    "image_path": "error_images/normal_746.jpg"
  }
];
