package com.mysite.demo.MongoDB.DataSchema;
import java.util.List;
import lombok.Data;
import lombok.Setter;
import lombok.Getter;

@Data
@Setter
@Getter
public class TimeData {
    private String day;
    private List<String> work_time;
    private List<String> break_time;
    private String description;
}
