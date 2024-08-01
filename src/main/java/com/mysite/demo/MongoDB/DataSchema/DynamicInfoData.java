package com.mysite.demo.MongoDB.DataSchema;

import java.util.List;
import java.util.Map;

import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;
import org.springframework.data.mongodb.core.mapping.Field;

import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import lombok.Getter;

@Document(collection = "dynamicInfo")
@NoArgsConstructor
@AllArgsConstructor
@Getter
@Data
public class DynamicInfoData {
    @Id
    private String _id;

    @Field("id")
    private String id;

    @Field("disk")
    private String disk;

    @Field("path")
    private String path;

    @Field("timeInfo")
    private Map<String, TimeData> seller_name;

    @Field("treat_cate")
    List<String> category;
}
