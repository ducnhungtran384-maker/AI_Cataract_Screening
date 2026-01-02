// 两个模型共同判错的图片列表（顽固错误）
const OVERLAP_ERRORS = [
  "1171.jpg",
  "1242.jpg",
  "1292.jpg",
  "1391.jpg",
  "1580.jpg",
  "1684.jpg",
  "2161.jpg",
  "2356.jpg",
  "2408.jpg",
  "3874.jpg"
];

// 统计信息
const ERROR_STATS = {
  finalmodel: {
    total: 23,
    unique: 13,  // 只有finalmodel错的
    overlap: 10  // 两者都错的
  },
  pytorch: {
    total: 37,
    unique: 27,  // 只有pytorch错的
    overlap: 10  // 两者都错的
  }
};
