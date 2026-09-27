-- 1. 仓库
CREATE TABLE warehouses (
    warehouse_id   INT          PRIMARY KEY AUTO_INCREMENT COMMENT '仓库编号',
    warehouse_name VARCHAR(50)  NOT NULL COMMENT '仓库名称',
    city           VARCHAR(30)  NOT NULL COMMENT '所在城市',
    area_sqm       INT          NOT NULL COMMENT '面积(平方米)',
    manager        VARCHAR(30)  NOT NULL COMMENT '负责人'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='仓库';

-- 2. 商品
CREATE TABLE products (
    sku          VARCHAR(20)   PRIMARY KEY COMMENT 'SKU编码',
    product_name VARCHAR(100)  NOT NULL COMMENT '商品名称',
    category     VARCHAR(30)   NOT NULL COMMENT '类目',
    unit_price   DECIMAL(10,2) NOT NULL COMMENT '单价(元)',
    volume_l     DECIMAL(8,2)  NOT NULL COMMENT '体积(升)',
    weight_kg    DECIMAL(8,2)  NOT NULL COMMENT '重量(千克)'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='商品SKU';

-- 3. 库存
CREATE TABLE inventory (
    inventory_id INT         PRIMARY KEY AUTO_INCREMENT COMMENT '库存记录编号',
    warehouse_id INT         NOT NULL COMMENT '仓库编号',
    sku          VARCHAR(20) NOT NULL COMMENT 'SKU编码',
    stock_qty    INT         NOT NULL COMMENT '当前库存件数',
    safety_stock INT         NOT NULL COMMENT '安全库存线',
    updated_at   DATETIME    NOT NULL COMMENT '更新时间',
    UNIQUE KEY uk_wh_sku (warehouse_id, sku),
    CONSTRAINT fk_inv_wh  FOREIGN KEY (warehouse_id) REFERENCES warehouses(warehouse_id),
    CONSTRAINT fk_inv_sku FOREIGN KEY (sku)          REFERENCES products(sku)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='库存';

-- 4. 入库单
CREATE TABLE inbound_orders (
    inbound_id   VARCHAR(20) PRIMARY KEY COMMENT '入库单号',
    warehouse_id INT         NOT NULL COMMENT '仓库编号',
    sku          VARCHAR(20) NOT NULL COMMENT 'SKU编码',
    quantity     INT         NOT NULL COMMENT '入库数量',
    inbound_time DATETIME    NOT NULL COMMENT '入库时间',
    supplier     VARCHAR(50) NOT NULL COMMENT '供应商',
    CONSTRAINT fk_in_wh  FOREIGN KEY (warehouse_id) REFERENCES warehouses(warehouse_id),
    CONSTRAINT fk_in_sku FOREIGN KEY (sku)          REFERENCES products(sku)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='入库单';

-- 5. 出库单
CREATE TABLE outbound_orders (
    outbound_id   VARCHAR(20) PRIMARY KEY COMMENT '出库单号',
    warehouse_id  INT         NOT NULL COMMENT '仓库编号',
    sku           VARCHAR(20) NOT NULL COMMENT 'SKU编码',
    quantity      INT         NOT NULL COMMENT '出库数量',
    outbound_time DATETIME    NOT NULL COMMENT '出库时间',
    customer      VARCHAR(50) NOT NULL COMMENT '客户',
    carrier       VARCHAR(30) NOT NULL COMMENT '承运商',
    CONSTRAINT fk_out_wh  FOREIGN KEY (warehouse_id) REFERENCES warehouses(warehouse_id),
    CONSTRAINT fk_out_sku FOREIGN KEY (sku)          REFERENCES products(sku)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='出库单';

-- 6. 运单
CREATE TABLE shipments (
    shipment_id  VARCHAR(20) PRIMARY KEY COMMENT '运单号',
    outbound_id  VARCHAR(20) NOT NULL COMMENT '出库单号',
    carrier      VARCHAR(30) NOT NULL COMMENT '承运商',
    ship_time    DATETIME    NOT NULL COMMENT '发货时间',
    deliver_time DATETIME    NULL     COMMENT '签收时间(未签收为空)',
    status       VARCHAR(10) NOT NULL COMMENT '状态',
    CONSTRAINT fk_ship_out FOREIGN KEY (outbound_id) REFERENCES outbound_orders(outbound_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='运单';