
from dataclasses import dataclass

@dataclass
class LoadConfig:

    EXAMPLE_PRICE = [
        {
            "input_text":"robot hút bụi nào có tính năng hẹn giờ và hệ thống điều hướng AIVI 3D giá rẻ nhất",
            "object":["robot hút bụi"],
            "power":"",           
            "price":["giá rẻ nhất"],
            "weight":"",
            "volume":"",
            "specifications":"tính năng hẹn giờ và hệ thống điều hướng AIVI 3D"
        },
        {
            "input_text":"Tôi muốn tìm điều hòa giá 10tr có tính năng inverter, diện tích lam mát khoảng 20m2",
            "object":["điều hòa"],
            "power":"",           
            "price":["giá 10tr"],
            "weight":"",
            "volume":"",
            "specifications":"tính năng inverter, diện tích lam mát khoảng 20m2"
        },
        {
            "input_text":"Tôi cần điều hòa Carrier 1 chiều Inverter 12.000 BTU/h (1.5 HP) - Model 2023 giá 11.5tr",
            "object":["điều hòa Carrier 1 chiều Inverter 12.000 BTU/h (1.5 HP) - Model 2023"],
            "power":"",           
            "price":["giá 11.5tr"],
            "weight":"",
            "volume":"",
            "specifications":""
        },
        {
            "input_text":"lò vi sóng 5 nghìn đồng",
            "object":["lò vi sóng"],
            "power":"",           
            "price":["5 nghìn đồng"],
            "weight":"",
            "volume":"",
            "specifications":""
        },
        {
            "input_text":"Tôi muốn mua bàn là giá 500k và máy sấy 100k",
            "object":["bàn là", "máy sấy"],
            "power":"",           
            "price":["giá 500k", "100k"],
            "weight":"",
            "volume":"",
            "specifications":""
        },
        {
            "input_text":"Điều hòa rẻ",
            "object":["điều hòa"],
            "power":"",           
            "price":["rẻ"],
            "weight":"",
            "volume":"",
            "specifications":""
        },
        {
            "input_text":"Máy giặt khoảng 20tr",
            "object":["máy giặt "],
            "power":"",           
            "price":["khoảng 20tr"],
            "weight":"",
            "volume":"",
            "specifications":""
        },
        {
            "input_text":"đèn năng lượng mặt trời có đắt nhất, có diện tích chiếu sáng 100m2",
            "object":["đèn năng lượng mặt trời"],
            "power":"",           
            "price":["đắt nhất"],
            "weight":"",
            "volume":"",
            "specifications":"diện tích chiếu sáng 100m2"
        },
        {
            "input_text":"bếp từ có giá thấp nhất nhưng tiết kiệm điện",
            "object":["bếp từ"],
            "power":"",           
            "price":["giá thấp nhất"],
            "weight":"",
            "volume":"",
            "specifications":""
        },
        {
            "input_text":"robot hút bụi có giá thành 3 tỉ, điều hòa có giá 5tr",
            "object":["robot hút bụi", "điều hòa"],
            "power":"",           
            "price":["giá 3 tỉ", "5tr"],
            "weight":"",
            "volume":"",
            "specifications":""
        },
        {
            "input_text":"Tôi cần tìm đèn năng lượng mặt trời có cân nặng tầm 3kg có dưới 1tr, thời gian chiếu sáng 20h",
            "object":["đèn năng lượng mặt trời"],
            "power":"",           
            "price":["dưới 1tr"],
            "weight":"3kg",
            "volume":"",
            "specifications":"thời gian chiếu sáng 20h"
        }
        ]

    EXAMPLE_POWER =  [
        {
            "input_text":"đèn năng lượng mặt trời công suất 90W",
            "object":["đèn năng lượng mặt trời"],
            "power":"90W",           
            "price":[""],
            "weight":"",
            "volume":"",
            "specifications":""
        },
        {
            "input_text":"Bếp từ nào có công suất lớn nhất",
            "object":["bếp từ"],
            "power":"lớn nhất",           
            "price":[""],
            "weight":"",
            "volume":"",
            "specifications":""
        },
        {
            "input_text":"tôi cần tủ lạnh công suất trên 1000kw",
            "object":["tủ lạnh"],
            "power":"trên 1000kw",           
            "price":[""],
            "weight":"",
            "volume":"",
            "specifications":""
        },
        {
            "input_text":"Điều hòa Daikin 2 chiều Inverter 2023 bao nhiêu w",
            "object":["Điều hòa Daikin 2 chiều Inverter 2023"],
            "power":"",           
            "price":[""],
            "weight":"",
            "volume":"",
            "specifications":""
        },
        {
            "input_text":"tôi cần tìm đèn năng lượng bàn chải rời thể 400w",
            "object":["đèn năng lượng bàn chải rời thể "],
            "power":"400w",           
            "price":[""],
            "weight":"",
            "volume":"",
            "specifications":""
        },
        {
            "input_text":"cho tôi xem sản phẩm bình nước nóng có công suất tầm 700w",
            "object":["bình nước nóng"],
            "power":"700w",           
            "price":[""],
            "weight":"",
            "volume":"",
            "specifications":""
        },
        {
            "input_text":"với công suất 300w thì có những sản phẩm nồi cơm điện nào",
            "object":["nồi cơm điện"],
            "power":"300w",           
            "price":[""],
            "weight":"",
            "volume":"",
            "specifications":""
        },
        {
            "input_text":"đèn năng lượng mặt trời nào có công suất nhỏ",
            "object":["đèn năng lượng mặt trời"],
            "power":"nhỏ",           
            "price":[""],
            "weight":"",
            "volume":"",
            "specifications":""
        },
        {
            "input_text":"Diện tích chiếu sáng đèn năng lượng mặt trời công suất 90W",
            "object":["đèn năng lượng mặt trời"],
            "power":"90w",           
            "price":[""],
            "weight":"",
            "volume":"",
            "specifications":"Diện tích chiếu sáng"
        },
        {
            "input_text":"Bên bán có bán điều hòa có công suất 12000w có tính năng Inverter",
            "object":["điều hòa"],
            "power":"12000w",           
            "price":[""],
            "weight":"",
            "volume":"",
            "specifications":"tính năng Inverter"
        }]

    EXAMPLE_VOLUME = [
        {
            "input_text":"cho tôi bình nước nóng có dung tích 30 lít",
            "object":["bình nước nóng"],
            "power":"",           
            "price":[""],
            "weight":"",
            "volume":"30 lít",
            "specifications":""
        },
        {
            "input_text":"máy giặt nào có thể tích từ 5 lít trở lên",
            "object":["máy giặt"],
            "power":"",           
            "price":[""],
            "weight":"",
            "volume":"từ 5 lít",
            "specifications":""
        },
        {
            "input_text":"lò nướng KALITE 4 lít",
            "object":["lò nướng KALITE"],
            "power":"",           
            "price":[""],
            "weight":"",
            "volume":"4 lít",
            "specifications":""
        },
        {
            "input_text":"bình nước nóng nào có dung tích trên 500ml",
            "object":["bình nước nóng"],
            "power":"",           
            "price":[""],
            "weight":"",
            "volume":"trên 500ml",
            "specifications":""
        },
        {
            "input_text":"Có máy giặt nào có dung tích lớn hơn 10l không",
            "object":["máy giặt"],
            "power":"",           
            "price":[""],
            "weight":"",
            "volume":"lớn hơn 10l",
            "specifications":""
        },
        {
            "input_text":"Sản phẩm bàn là loại hơi nước xanh dương nhạt nào 5 lít",
            "object":["bàn là"],
            "power":"",           
            "price":[""],
            "weight":"",
            "volume":"5 lít",
            "specifications":"hơi nước xanh dương nhạt"
        },
        {
            "input_text":"tôi cần tìm máy giặt có dung tích lớn",
            "object":["máy giặt"],
            "power":"",           
            "price":[""],
            "weight":"",
            "volume":"dung tích lớn",
            "specifications":""
        },
        {
            "input_text":"bình nước nóng nào đang có thể tích nhỏ",
            "object":["bình nước nóng"],
            "power":"",           
            "price":[""],
            "weight":"",
            "volume":"thể tích nhỏ",
            "specifications":""
        }]

    EXAMPLE_WEIGHT =  [
        {
            "input_text":"đèn năng lượng mặt trời có cân nặng tầm 3kg",
            "object":["đèn năng lượng mặt trời"],
            "power":"",           
            "price":[""],
            "weight":"3kg",
            "volume":"",
            "specifications":""
        },
        {
            "input_text":"cho tôi máy giặt có khối lượng 13kg",
            "object":["máy giặt"],
            "power":"",           
            "price":[""],
            "weight":"13kg",
            "volume":"",
            "specifications":""
        },
        {
            "input_text":"cho tôi robot hút bụi 5g",
            "object":["robot hút bụi"],
            "power":"",           
            "price":[""],
            "weight":"5g",
            "volume":"",
            "specifications":""
        },
        {
            "input_text":"máy giặt có sức chứa 3000g",
            "object":["máy giặt"],
            "power":"",           
            "price":[""],
            "weight":"3000g",
            "volume":"",
            "specifications":""
        },
        {
            "input_text":"tôi cần tìm Điều hòa Carrier 2 chiều Inverter - Công suất 9.000 BTU/h (1 HP) - Model 2023 có cân nặng 10kg",
            "object":["Điều hòa Carrier 2 chiều Inverter"],
            "power":"",           
            "price":[""],
            "weight":"10kg",
            "volume":"",
            "specifications":""
        },
        {
            "input_text":"cho xem lò nướng nặng nhất",
            "object":["lò nướng"],
            "power":"",           
            "price":[""],
            "weight":"nặng nhất",
            "volume":"",
            "specifications":""
        },
        {
            "input_text":"tìm robot hút bụi nhẹ ",
            "object":["robot hút bụi"],
            "power":"",           
            "price":[""],
            "weight":"nhẹ",
            "volume":"",
            "specifications":""
        },
        {
            "input_text":"bàn là có khối lượng nhỏ",
            "object":["bàn là"],
            "power":"",           
            "price":[""],
            "weight":"khối lượng nhỏ",
            "volume":"",
            "specifications":""
        }]


    EXAMPLE_QUANTITY = [
        {
            "input_text":"bao nhiêu điều hòa giá 10tr",
            "object":["điều hòa"],
            "power":"",           
            "price":["10tr"],
            "weight":"",
            "volume":"",
            "specifications":"bao nhiêu"
        },
        {
            "input_text":"số lượng lò vi sóng giá",
            "object":["lò vi sóng"],
            "power":"",           
            "price":[""],
            "weight":"",
            "volume":"",
            "specifications":"số lượng"
        },
        {
            "input_text":"có mấy cái đèn năng lượng mặt trời có cân nặng tầm 3kg có giá dưới 1tr",
            "object":["đèn năng lượng mặt trời"],
            "power":"",           
            "price":["dưới 1tr"],
            "weight":"3kg",
            "volume":"",
            "specifications":"mấy"
        },
        {
            "input_text":"bao nhiêu điều hòa có công suất trên 9000BTU, giá trên 10 triệu, cân nặng dưới 10kg",
            "object":["điều hòa"],
            "power":"9000BTU",           
            "price":["trên 10 triệu"],
            "weight":"dưới 10kg",
            "volume":"",
            "specifications":"bao nhiêu"
        },
        {
            "input_text":"số lượng bàn là giá 500k và máy sấy 100k",
            "object":["bàn là"],
            "power":"",           
            "price":["500k", "100k"],
            "weight":"",
            "volume":"",
            "specifications":"số lượng"
        },
        {
            "input_text":"tổng số đèn năng lượng mặt trời có câm nặng tầm 3kg có giá dưới 1tr",
            "object":["đèn năng lượng mặt trời"],
            "power":"",           
            "price":["dưới 1tr"],
            "weight":"tầm 3kg",
            "volume":"",
            "specifications":"tổng số"
        },
        {
            "input_text":"cho tôi xem bên bạn bán bao nhiêu máy xay",
            "object":["máy xay"],
            "power":"",           
            "price":[""],
            "weight":"",
            "volume":"",
            "specifications":"bao nhiêu"
        },
        {
            "input_text":"số lượng điều hòa giá 10tr",
            "object":["điều hòa"],
            "power":"",           
            "price":["10tr"],
            "weight":"",
            "volume":"",
            "specifications":"số lượng"
        }]

FEWSHOT_CONFIG = LoadConfig()