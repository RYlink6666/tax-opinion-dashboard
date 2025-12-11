# -*- coding: utf-8 -*-
"""
Generate mock opinion data for quick testing
Real data can replace this after collection
"""

import json
import random
from datetime import datetime

# Mock opinion templates based on real cross-border e-commerce tax discussions
MOCK_TEMPLATES = {
    '0110': [
        '我们的香港公司战略决策都在国内，财务申报也在国内，会不会被认定为税收居民？',
        '香港公司人员在国内，怎么避免被认定为虚拟公司？',
        '香港空壳公司0申报，被税务局查了怎么办？',
        '实质管理地在国内，香港公司还有意义吗？',
        '跨境公司架构，怎样才能合法避税？',
        '香港子公司没有真实业务，只是财务中心，这样合规吗？',
        'ODI备案后，香港公司能不能回避增值税？',
        '我的香港公司主要是法律身份，所有决策在深圳总部，这样的话有税收居民认定风险吗？',
        '境外公司控股国内，怎样才能避免被认定为中国税收居民？',
        '新加坡公司代理采购，国内销售，这个模式还能用吗？',
    ],
    
    '9610': [
        '9610备案已经3个月还没批下来，物流公司说不清楚手续，很焦虑',
        '9610备案困难，政府部门效率太低',
        '三单对碰的要求太严格了，数据很难完全匹配',
        '9610模式的核定征收政策什么时候能明确？',
        '备案流程太复杂，找不到懂的人指导',
        '海外仓的物流企业不配合，9610很难继续',
        '退运怎么操作？系统里找不到选项',
        '9610的增值税和所得税口径不一致，被查出来要补多少税？',
        '小包裹用9610，大包裹用什么方式？',
        '9610和9810能混用吗？混用了会有问题吗？',
    ],
    
    '9710': [
        '9710的身份验证怎么搞？在阿里国际站和速卖通都有店',
        'B2B订单怎么证明是真实的而不是虚假订单？',
        '9710对买家的身份有什么要求？',
        '线上订单凭证被税务部门质疑怎么办？',
        '一个人名义多个购买者，这样符合9710的身份要求吗？',
        '跨境电商平台上的订单能不能当作9710的凭证？',
        '速卖通订单能用9710吗？还是只能用9610？',
        '9710没有核定征收优惠了，现在税负有多高？',
        '多平台混合运营，9710怎么核算？',
        '9710订单必须是全额支付吗？',
    ],
    
    '9810': [
        '9810海外仓操作，库存和销售数据始终对不上，被查过一次补了200万',
        '9810出了4次，卖的数量和报关数对不上怎么办？',
        '多平台混合销售，库存核销特别困难',
        '海外仓报价无法预测，财务算不清楚',
        '9810的离境退税手续费太高了',
        '海外仓滚动发货，怎么跟报关数据对应？',
        '多个国家的海外仓，库存怎么统一管理？',
        '9810的库存在海外，国内怎么审计？',
        '报关价格和实际销售价格差异大，有税务风险吗？',
        '海外仓存货的增值税怎么抵扣？',
    ],
    
    '1039': [
        '从1039切换到其他模式，因为规模超过500万',
        '1039规模不能超过500万了，我们现在规模700万，怎么办？',
        '市场采购模式被收紧了，还能继续用吗？',
        '义乌市场采购，拼箱会有风险吗？',
        '外综服操作不了了，1039还有出路吗？',
        '1039无发票，但销售有发票，这个矛盾怎么解决？',
        '小商户能用1039吗？还是只能企业用？',
        '1039的免税优惠还有吗？',
        '超过500万规模，不能继续用1039，现在很纠结选哪个模式',
        '1039和9610哪个更合规？',
    ],
    
    'Temu': [
        'Temu规模到500万后，13%增值税真的交不起',
        'Temu做到500万规模，税负爆表，在考虑独立模式',
        'Temu全托管，内销视同的税率太高了',
        'Temu平台定价权在平台，我们无法控制成本',
        'Temu一开始规模小，税负可接受，但做大了就不行了',
        '无库存模式的增值税怎么计算？',
        '平台不开发票怎么抵扣进项税？',
        'Temu卖家超规模后的出路在哪里？',
        '全托管模式转向独立运营有多难？',
        'Temu税务筹划有什么办法吗？',
    ],
    
    '政策': [
        '新政策很公平，规范了市场，我们已经调整了定价',
        '跨境电商增值税政策需要更多企业参与的机会',
        '政策执行还有很多不清楚的地方',
        '政府部门的政策指导不一致，各个部门说的不一样',
        '需要更多关于税收合规的官方指导',
        '政策变化太快，企业跟不上',
        '希望税务部门能更通俗地解释政策',
        '补税的滞纳金太重了',
        '先前的政策优惠都取消了，现在做跨境很困难',
        '税收征管越来越严，企业合规成本增加了',
    ],
    
    '补税': [
        '被税务查了，补税了300万，现在每个月都在等通知',
        '增值税和所得税数据不符，被查出来补了800万',
        '已经被查过两次了，每次都查出新问题，又要补税',
        '主动补税200万，从长期看这是正确的',
        '被查到偷税漏税了，处罚加补税共150万',
        '补税后公司现金流紧张',
        '多次被查，累计补税超过1000万',
        '咨询了税务顾问，准备主动补税',
        '补税加滞纳金，总共要交500万',
        '已经补过税了，现在等着看还会不会被二次查',
    ],
}

class MockDataGenerator:
    """Mock data generator"""
    
    def __init__(self, count=5000):
        self.count = count
        self.data = []
    
    def generate(self):
        """Generate mock data"""
        print("[*] Generating mock opinion data...")
        
        all_templates = []
        for category, templates in MOCK_TEMPLATES.items():
            for template in templates:
                all_templates.append({
                    'category': category,
                    'text': template
                })
        
        # Cycle through templates to generate required count
        for i in range(self.count):
            template = all_templates[i % len(all_templates)]
            
            # Random variation to avoid exact duplicates
            text = template['text']
            if random.random() > 0.7:
                text = text + random.choice([
                    '，求解答',
                    '，有人遇到过吗？',
                    '，怎么处理？',
                    '，太困难了',
                    '，没有办法',
                ])
            
            self.data.append({
                'id': i + 1,
                'platform': random.choice(['weibo', 'zhihu', 'xiaohongshu']),
                'category': template['category'],
                'text': text,
                'collected_at': datetime.now().isoformat()
            })
        
        print("[+] Generated %d mock opinions" % len(self.data))
        return self.data
    
    def save_txt(self, filename='opinions_clean_5000.txt'):
        """Save as TXT"""
        with open(filename, 'w', encoding='utf-8') as f:
            for item in self.data:
                f.write(item['text'] + '\n')
        print("[+] Saved to %s" % filename)
    
    def save_json(self, filename='opinions_clean_5000.json'):
        """Save as JSON"""
        output = {
            'metadata': {
                'total': len(self.data),
                'type': 'mock_data_for_testing',
                'created_at': datetime.now().isoformat(),
                'note': 'Mock data for quick testing. Replace with real data after collection.'
            },
            'data': [item['text'] for item in self.data]
        }
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        print("[+] Saved to %s" % filename)
    
    def save_csv(self, filename='opinions_clean_5000.csv'):
        """Save as CSV"""
        import csv
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['id', 'platform', 'category', 'text'])
            writer.writeheader()
            writer.writerows(self.data)
        print("[+] Saved to %s" % filename)
    
    def report(self):
        """Print report"""
        from collections import Counter
        
        print("\n" + "=" * 70)
        print("Data Generation Report")
        print("=" * 70)
        
        categories = Counter([item['category'] for item in self.data])
        platforms = Counter([item['platform'] for item in self.data])
        
        print("\nTotal: %d" % len(self.data))
        
        print("\nBy Category:")
        for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            pct = count / len(self.data) * 100
            print("  %-15s: %4d (%.1f%%)" % (cat, count, pct))
        
        print("\nBy Platform:")
        for plat, count in platforms.items():
            pct = count / len(self.data) * 100
            print("  %-15s: %4d (%.1f%%)" % (plat, count, pct))
        
        print("\nNOTE: This is mock data for testing LLM analysis flow.")
        print("      Replace with real data after collection.\n")
        print("=" * 70 + "\n")


if __name__ == "__main__":
    generator = MockDataGenerator(count=5000)
    generator.generate()
    generator.save_txt()
    generator.save_json()
    generator.save_csv()
    generator.report()
    
    print("[SUCCESS] Mock data ready for LLM analysis!")
